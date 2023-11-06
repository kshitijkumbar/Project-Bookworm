from transformers import (AutoProcessor, 
                          Blip2ForConditionalGeneration, 
                          AutoTokenizer, 
                          pipeline, 
                          AutoConfig,
                          AutoModelForCausalLM,
                          BitsAndBytesConfig
                          )

import torch

class ModelLoader():
    
    def __init__(self, text_model_config = None, caption_model_config = None, diffusion_model_config = None):
        self.text_model_config = text_model_config
        self.caption_model_config = caption_model_config
        self.diffusion_model_config = diffusion_model_config
        self.default_bnb_config = BitsAndBytesConfig(
                                                load_in_4bit=True,
                                                bnb_4bit_quant_type='nf4',
                                                bnb_4bit_use_double_quant=True,
                                                bnb_4bit_compute_dtype=torch.bfloat16
                                            )
    
    def getTextModel(self, get_tokenizer=True):
        """
            Get Text LLM for QA/Chat
        """
        model = None
        if self.text_model_config is None:
            model_id = "meta-llama/Llama-2-13b-chat-hf"
            model_config = AutoConfig.from_pretrained(
                model_id
            )

            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                trust_remote_code=True,
                config=model_config,
                quantization_config=self.default_bnb_config,
                device_map='auto'
            )
        else:
            pass
        
        if get_tokenizer:
            tokenizer = AutoTokenizer.from_pretrained(model_id)
        
        return model, tokenizer
    
    def getCaptionModel(self, get_processor=True):
        """
            Get Image Captioning Model for image based queries
        """
        model = None
        if self.caption_model_config is None:
        # # Caption Generation
            model = Blip2ForConditionalGeneration.from_pretrained("Salesforce/blip2-opt-2.7b", quantization_config = self.default_bnb_config, torch_dtype=torch.float16)
            if get_processor:
                processor = AutoProcessor.from_pretrained("Salesforce/blip2-opt-2.7b", quantization_config = self.default_bnb_config,)

        return model, processor
