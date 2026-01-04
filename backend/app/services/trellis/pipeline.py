import os
import io
from typing import Dict, Any, Optional, Callable, List
from pathlib import Path
from PIL import Image
import torch

from app.config import settings
from app.core.storage import storage_service


os.environ['SPCONV_ALGO'] = 'native'


class TRELLISPipeline:
    def __init__(self):
        self.image_pipeline = None
        self.text_pipeline = None
        self.device = settings.TRELLIS_DEVICE
        self._initialized = False

    def initialize(self):
        if self._initialized:
            return

        try:
            from trellis.pipelines import TrellisImageTo3DPipeline, TrellisTextTo3DPipeline
            from trellis.utils import render_utils, postprocessing_utils

            self.render_utils = render_utils
            self.postprocessing_utils = postprocessing_utils

            print(f"Loading TRELLIS image model from {settings.TRELLIS_MODEL_PATH}...")
            self.image_pipeline = TrellisImageTo3DPipeline.from_pretrained(
                settings.TRELLIS_MODEL_PATH
            )
            if self.device == "cuda":
                self.image_pipeline.cuda()

            print(f"Loading TRELLIS text model from {settings.TRELLIS_TEXT_MODEL_PATH}...")
            self.text_pipeline = TrellisTextTo3DPipeline.from_pretrained(
                settings.TRELLIS_TEXT_MODEL_PATH
            )
            if self.device == "cuda":
                self.text_pipeline.cuda()

            self._initialized = True
            print("TRELLIS pipelines initialized successfully")

        except ImportError as e:
            print(f"TRELLIS not installed: {e}")
            print("Running in mock mode for development")
            self._initialized = True

    def _get_sampler_params(self, resolution: str, params: Optional[Dict] = None) -> Dict:
        defaults = {
            "low": {"steps": 8, "cfg_strength": 7.5},
            "medium": {"steps": 12, "cfg_strength": 7.5},
            "high": {"steps": 20, "cfg_strength": 7.5}
        }

        result = defaults.get(resolution, defaults["medium"]).copy()

        if params:
            result.update(params)

        return result

    def generate_from_image(
        self,
        image_path: str,
        job_id: str,
        seed: Optional[int] = None,
        resolution: str = "medium",
        sparse_structure_sampler_params: Optional[Dict] = None,
        slat_sampler_params: Optional[Dict] = None,
        progress_callback: Optional[Callable[[int, str, int], None]] = None
    ) -> Dict[str, Any]:
        self.initialize()

        if progress_callback:
            progress_callback(10, "loading_image", 100)

        image = Image.open(image_path)

        if self.image_pipeline is None:
            return self._mock_generate(job_id, progress_callback)

        if progress_callback:
            progress_callback(20, "preprocessing", 100)

        ss_params = self._get_sampler_params(resolution, sparse_structure_sampler_params)
        slat_params = self._get_sampler_params(resolution, slat_sampler_params)

        if progress_callback:
            progress_callback(30, "generating_sparse_structure", 0)

        outputs = self.image_pipeline.run(
            image,
            seed=seed or 42,
            formats=["mesh", "gaussian"],
            preprocess_image=True,
            sparse_structure_sampler_params=ss_params,
            slat_sampler_params=slat_params
        )

        if progress_callback:
            progress_callback(70, "exporting", 0)

        return self._export_outputs(job_id, outputs, progress_callback)

    def generate_from_text(
        self,
        prompt: str,
        job_id: str,
        seed: Optional[int] = None,
        resolution: str = "medium",
        sparse_structure_sampler_params: Optional[Dict] = None,
        slat_sampler_params: Optional[Dict] = None,
        progress_callback: Optional[Callable[[int, str, int], None]] = None
    ) -> Dict[str, Any]:
        self.initialize()

        if progress_callback:
            progress_callback(10, "preparing_prompt", 100)

        if self.text_pipeline is None:
            return self._mock_generate(job_id, progress_callback)

        ss_params = self._get_sampler_params(resolution, sparse_structure_sampler_params)
        slat_params = self._get_sampler_params(resolution, slat_sampler_params)

        if progress_callback:
            progress_callback(30, "generating_sparse_structure", 0)

        outputs = self.text_pipeline.run(
            prompt,
            seed=seed or 42,
            formats=["mesh", "gaussian"],
            sparse_structure_sampler_params=ss_params,
            slat_sampler_params=slat_params
        )

        if progress_callback:
            progress_callback(70, "exporting", 0)

        return self._export_outputs(job_id, outputs, progress_callback)

    def _export_outputs(
        self,
        job_id: str,
        outputs: Dict,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        result = {
            "glb_path": None,
            "ply_path": None,
            "preview_path": None,
            "file_sizes": {}
        }

        try:
            if progress_callback:
                progress_callback(75, "exporting_glb", 0)

            glb = self.postprocessing_utils.to_glb(
                outputs['gaussian'][0],
                outputs['mesh'][0],
                simplify=0.95,
                texture_size=1024,
                verbose=False
            )

            glb_buffer = io.BytesIO()
            glb.export(glb_buffer, file_type='glb')
            glb_data = glb_buffer.getvalue()

            glb_path = storage_service.save_output_sync(job_id, glb_data, "glb")
            result["glb_path"] = glb_path
            result["file_sizes"]["glb"] = len(glb_data)

            if progress_callback:
                progress_callback(85, "exporting_ply", 0)

            ply_buffer = io.BytesIO()
            outputs['gaussian'][0].save_ply(ply_buffer)
            ply_data = ply_buffer.getvalue()

            ply_path = storage_service.save_output_sync(job_id, ply_data, "ply")
            result["ply_path"] = ply_path
            result["file_sizes"]["ply"] = len(ply_data)

            if progress_callback:
                progress_callback(95, "generating_preview", 0)

            try:
                video = self.render_utils.render_video(outputs['gaussian'][0], num_frames=1)
                if video and 'color' in video and len(video['color']) > 0:
                    preview_frame = video['color'][0]
                    preview_img = Image.fromarray(preview_frame)
                    preview_buffer = io.BytesIO()
                    preview_img.save(preview_buffer, format='PNG')
                    preview_data = preview_buffer.getvalue()
                    preview_path = storage_service.save_preview_sync(job_id, preview_data)
                    result["preview_path"] = preview_path
            except Exception as e:
                print(f"Failed to generate preview: {e}")

        except Exception as e:
            print(f"Export error: {e}")
            raise

        finally:
            if self.device == "cuda":
                torch.cuda.empty_cache()

        return result

    def _mock_generate(
        self,
        job_id: str,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        import time

        stages = [
            (20, "preprocessing", 100),
            (40, "generating_sparse_structure", 100),
            (60, "generating_slat", 100),
            (80, "exporting", 100),
            (95, "finalizing", 100)
        ]

        for progress, stage, stage_progress in stages:
            if progress_callback:
                progress_callback(progress, stage, stage_progress)
            time.sleep(0.5)

        mock_glb = b"mock_glb_content"
        mock_ply = b"mock_ply_content"

        glb_path = storage_service.save_output_sync(job_id, mock_glb, "glb")
        ply_path = storage_service.save_output_sync(job_id, mock_ply, "ply")

        return {
            "glb_path": glb_path,
            "ply_path": ply_path,
            "preview_path": None,
            "file_sizes": {
                "glb": len(mock_glb),
                "ply": len(mock_ply)
            }
        }


trellis_pipeline = TRELLISPipeline()
