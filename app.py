# ====================== ANIME 18+ FULL EXPLICIT (FREE COLAB) ======================
!pip install -q diffusers transformers accelerate gradio==3.50.2 torch torchvision pillow

import torch
import gradio as gr
from diffusers import StableDiffusionImg2ImgPipeline
from PIL import Image, ImageEnhance
import gc

# Model thiên NSFW hơn (vẫn chạy được T4 free)
model_id = "gsdf/Counterfeit-V3.0"   # Chi tiết + dễ ra explicit hơn Anything

pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    safety_checker=None,
    requires_safety_checker=False
)
pipe = pipe.to("cuda")
pipe.enable_attention_slicing()

def process_image(input_img, prompt, negative_prompt, strength, guidance, steps, 
                  brightness, contrast, saturation):
    if input_img is None:
        return None
    
    img = input_img.convert("RGB")
    if brightness != 1.0:
        img = ImageEnhance.Brightness(img).enhance(brightness)
    if contrast != 1.0:
        img = ImageEnhance.Contrast(img).enhance(contrast)
    if saturation != 1.0:
        img = ImageEnhance.Color(img).enhance(saturation)
    
    w, h = img.size
    max_size = 768
    if max(w, h) > max_size:
        ratio = max_size / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
    
    w, h = img.size
    w = (w // 8) * 8
    h = (h // 8) * 8
    img = img.resize((w, h), Image.LANCZOS)
    
    result = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        image=img,
        strength=strength,
        guidance_scale=guidance,
        num_inference_steps=int(steps),
        generator=torch.Generator(device="cuda").manual_seed(torch.randint(0, 2**32, (1,)).item())
    ).images[0]
    
    torch.cuda.empty_cache()
    gc.collect()
    return result

with gr.Blocks(title="Anime 18+ Explicit Editor") as demo:
    gr.Markdown("## Anime 18+ Explicit - Full nude (nipples + pussy)")
    
    with gr.Row():
        with gr.Column():
            input_img = gr.Image(type="pil", label="Upload ảnh")
            prompt = gr.Textbox(
                label="Prompt", 
                value="masterpiece, best quality, highly detailed, 1girl, completely nude, nipples, pussy, detailed vagina, detailed nipples, uncensored, beautiful detailed eyes, detailed skin, anime style, sharp focus",
                lines=4
            )
            negative_prompt = gr.Textbox(
                label="Negative Prompt",
                value="worst quality, low quality, clothed, dress, panties, bra, clothes, covered nipples, censored, mosaic, bar censor, bad anatomy, bad hands, missing fingers, extra digits, lowres, blurry, text, watermark, deformed",
                lines=3
            )
            strength = gr.Slider(0.45, 0.75, value=0.60, step=0.05, label="Strength (0.55-0.65 thường ra explicit tốt)")
            guidance = gr.Slider(6, 12, value=8, step=0.5, label="Guidance Scale")
            steps = gr.Slider(25, 40, value=32, step=1, label="Steps")
            
            with gr.Row():
                brightness = gr.Slider(0.7, 1.4, value=1.0, step=0.05, label="Độ sáng")
                contrast = gr.Slider(0.7, 1.4, value=1.0, step=0.05, label="Tương phản")
                saturation = gr.Slider(0.7, 1.4, value=1.0, step=0.05, label="Độ bão hòa")
            
            btn = gr.Button("Tạo ảnh Explicit", variant="primary")
        
        with gr.Column():
            output_img = gr.Image(label="Kết quả")
    
    btn.click(
        fn=process_image,
        inputs=[input_img, prompt, negative_prompt, strength, guidance, steps, 
                brightness, contrast, saturation],
        outputs=output_img
    )

demo.launch(share=True, debug=True)
