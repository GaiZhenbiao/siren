from asteroid.models import BaseModel

pre_trained_path = "./pretrained/ConvTasNet_Libri2Mix_sepnoisy_16k.bin"
mixture_path = "./MFS.wav"

model = BaseModel.from_pretrained(pre_trained_path)

model.separate(mixture_path, resample=True)
