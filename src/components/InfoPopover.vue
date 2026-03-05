<template>
  <div class="info-popover" role="dialog" aria-modal="false" aria-label="Information">
    <header>
      <h3>Info</h3>
      <IconButton label="Close" @click="emit('close')" />
    </header>

    <div class="info-popover__body">
      <section class="intro">
        <p>
          This interactive demo was built in the ScaDS.AI Leipzig Living Lab.
          It shows how a model can turn text and images into a common numerical representation (an embedding).
          These embeddings can then be compared, even if the inputs are different types of data.
        </p>
      </section>

      <section>
        <h4>Embeddings</h4>
        <p>
          Imagine meaning as a map: each input — a sentence, a paragraph, or an image — becomes a single point on a gigantic coordinate
          system. An embedding is simply the numeric address of that point: a long list of numbers that captures the input's essence.
        </p>
        <p>
          Because similar things tend to live near one another on this map, the embedding for "apple" will usually be much closer to
          "banana" than to "house". Proximity in the embedding space is a quick and reliable way to measure semantic similarity.
        </p>
        <p>
          Embeddings power many common tasks: semantic search ("find items like this"), clustering (grouping similar examples),
          recommendation, and reranking. They are not just a retrieval trick — they're a core representation that modern models use to
          reason about content.
        </p>
        <p>
          Inside an LLM pipeline the flow typically looks like: tokenize the input, convert tokens into embeddings, and feed those
          embeddings into the transformer layers. In short: embeddings are the numeric language the model speaks — without them the
          rest of the system wouldn't have anything compact and comparable to work with.
        </p>
      </section>

      <section>
        <h4>Rendering the waterlilies</h4>
        <p>
          The waterlily shape is generated from the embedding values. The numbers are mapped to a smooth outline so that each input produces
          a consistent, unique shape.
        </p>
        <p>
          Color is also derived from the embedding. The mapping is limited to a pink-to-white range.
        </p>
      </section>

      <section>
        <h4>Placing waterlilies on the pond (PCA)</h4>
        <p>
          Embeddings live in a space with hundreds of dimensions — far more than we can draw. To show them on a flat pond, we need a smart
          way to compress that space down to two coordinates without losing the overall structure.
        </p>
        <p>
          PCA (principal component analysis) does exactly that. It finds the directions where the data varies the most and projects every
          embedding onto those axes. The result is a 2D sketch of the original space: not perfect, but often good enough to preserve
          neighborhoods, so similar inputs still land near each other.
        </p>
      </section>

      <section>
        <h4>The Modality Gap</h4>
        <p>
          The 2D picture you see here is the result of the PCA projection described above. Once we lay the embeddings out on this flat
          map, a characteristic pattern often appears: text points and image points drift into different regions.
        </p>
        <p>
          This spatial separation is called the modality gap. It means that even when a sentence and an image describe the same concept,
          their vectors may not end up as close as we would hope, which weakens cross‑modal search and comparison.
        </p>
        <p>
          A common way to visualize this is a stretched or truncated shape, with text on one side and images on the other:
        </p>
        <figure style="margin:10px 0 0;">
          <img src="/blogpost/modality_gap.png" alt="Modality gap visualization" style="max-width:100%; border-radius:8px;" />
          <figcaption style="font-size:0.85rem; color:rgba(29,41,51,0.66); margin-top:6px;">
            Source: https://itstedpark.medium.com/building-an-intelligent-pdf-chatbot-with-gpt-4-langchain-and-gradio-f6aa1c65d394
          </figcaption>
        </figure>
      </section>
      <section class="tech-sep">
        <h4>Multimodal embeddings — CLIP</h4>
        <p>
          OpenAI's CLIP model teaches images and text to meet in the middle. It learns a shared vector space by pulling matching captions
          and pictures together and pushing mismatches apart. The payoff is simple: a sentence and an image that describe the same thing
          end up nearby, which makes cross‑modal comparison feel natural.
        </p>
        <img
          class="info-popover__gif"
          src="/blogpost/clip_embeddings.gif"
          alt="CLIP encoding of text and images into shared embeddings"
          loading="lazy"
        />
        <p>
          Want the deep dive? Here is OpenAI's writeup on CLIP:
          <a href="https://openai.com/research/clip" target="_blank" rel="noreferrer">openai.com/research/clip</a>
        </p>

        <h4>Tech</h4>
        <p>
          Everything runs in your browser. There is no server-side computation and your inputs are not sent anywhere by this app.
        </p>
        <p>
          Embeddings are computed with
          <a href="https://github.com/huggingface/transformers.js" target="_blank" rel="noreferrer">Transformers.js</a>, running a
          <a href="https://openai.com/index/clip/" target="_blank" rel="noreferrer">CLIP</a> model locally.
        </p>
        <p>
          Transformer.js uses browser features like WebAssembly (WASM) and WebGPU/WebGL (depending on the device) to run the model.
          Performance depends on your browser and hardware.
        </p>
        <h5>What happens when you press “Grow”</h5>
        <p>
          Text is tokenized into integer IDs. Images are resized and normalized.
          Both are passed through CLIP to produce an embedding vector.
          The app then derives a waterlily shape and color from the numbers and renders the waterlily as an SVG shape.
        </p>
        <p>
          When you press “Plant”, the app updates the PCA layout to compute positions for all waterlilies on the pond.
        </p>
        <h5>Model download and caching</h5>
        <p>
          The first time you use the demo, the model files may be downloaded to your browser.
          After that, your browser can cache them so that future runs are faster.
        </p>
        <h5>Data handling</h5>
        <p>
          The app does not upload your text or images.
          If you choose an image file, the browser creates a local object URL so the image can be displayed and processed on your device.
        </p>
        <p>
          The embeddings that are produced are only kept in memory during the app's runtime — represented as JSON-like structures —
          and are not permanently stored or sent to any server.
        </p>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import IconButton from './IconButton.vue'

const emit = defineEmits<{
  (event: 'close'): void
}>()
</script>

<style scoped>
.info-popover__gif {
  width: 100%;
  max-width: 560px;
  display: block;
  margin: 12px auto 0;
  border-radius: 10px;
}
</style>
