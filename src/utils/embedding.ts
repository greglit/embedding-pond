import {
  AutoProcessor,
  AutoTokenizer,
  CLIPTextModelWithProjection,
  CLIPVisionModelWithProjection,
  RawImage,
  env,
} from '@huggingface/transformers'

let tokenizer: Awaited<ReturnType<typeof AutoTokenizer.from_pretrained>> | null = null
let processor: Awaited<ReturnType<typeof AutoProcessor.from_pretrained>> | null = null
let textModel: Awaited<ReturnType<typeof CLIPTextModelWithProjection.from_pretrained>> | null = null
let visionModel: Awaited<ReturnType<typeof CLIPVisionModelWithProjection.from_pretrained>> | null = null

env.allowLocalModels = false
env.useBrowserCache = true

const MODEL_ID = 'Xenova/clip-vit-base-patch32'

const getClipTextStack = async () => {
  if (!tokenizer) {
    tokenizer = await AutoTokenizer.from_pretrained(MODEL_ID)
  }
  if (!textModel) {
    textModel = await CLIPTextModelWithProjection.from_pretrained(MODEL_ID)
  }
  return { tokenizer, textModel }
}

const getClipVisionStack = async () => {
  if (!processor) {
    processor = await AutoProcessor.from_pretrained(MODEL_ID)
  }
  if (!visionModel) {
    visionModel = await CLIPVisionModelWithProjection.from_pretrained(MODEL_ID)
  }
  return { processor, visionModel }
}

const normalize = (vector: Float32Array) => {
  let sum = 0
  for (const value of vector) sum += value * value
  const norm = Math.sqrt(sum) || 1
  return Array.from(vector, (value) => value / norm)
}

export const computeEmbedding = async (type: 'text' | 'image', data: string) => {
  if (type === 'text') {
    const { tokenizer: clipTokenizer, textModel: clipTextModel } = await getClipTextStack()
    const textInputs = clipTokenizer([data], { padding: true, truncation: true })
    const { text_embeds } = await clipTextModel(textInputs)
    return normalize(text_embeds.data)
  }

  const { processor: clipProcessor, visionModel: clipVisionModel } = await getClipVisionStack()
  const image = await RawImage.fromURL(data)
  const imageInputs = await clipProcessor(image)
  const { image_embeds } = await clipVisionModel(imageInputs)
  return normalize(image_embeds.data)
}
