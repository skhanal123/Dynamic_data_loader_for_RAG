from transformers import AutoProcessor, AutoModelForImageTextToText
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
model = AutoModelForImageTextToText.from_pretrained(
    "stepfun-ai/GOT-OCR-2.0-hf", device_map=device
)
processor = AutoProcessor.from_pretrained("stepfun-ai/GOT-OCR-2.0-hf")


def extract_image_data_got_ocr2(image_path):

    inputs = processor(image_path, return_tensors="pt").to(device)

    generate_ids = model.generate(
        **inputs,
        do_sample=False,
        tokenizer=processor.tokenizer,
        stop_strings="<|im_end|>",
        max_new_tokens=4096,
    )

    extracted_text = str(
        processor.decode(
            generate_ids[0, inputs["input_ids"].shape[1] :], skip_special_tokens=True
        )
    )

    return extracted_text
