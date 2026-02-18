<template>
  <div class="info-popover" role="dialog" aria-modal="false" aria-label="Information">
    <header>
      <h3>Info</h3>
      <IconButton label="Close" @click="emit('close')" />
    </header>

    <div class="info-popover__body">
      <section>
        <p>
          This interactive demo was built in the ScaDS.AI Leipzig Living Lab.
          It shows how a model can turn text and images into a common numerical representation (an embedding).
          These embeddings can then be compared, even if the inputs are different types of data.
        </p>
      </section>

      <section>
        <h4>Embeddings</h4>
        <p>
          An embedding is a long list of numbers (a vector). It is used as a compact representation of an input, for example a sentence or
          an image.
        </p>
        <p>
          A useful embedding has this property: inputs with similar meaning get vectors that are close to each other.
        </p>
        <p>
          Many AI systems need numbers so they can compare, search, or group data.
          Embeddings are commonly used for semantic search ("find something like this") and for clustering ("group similar things").
          In LLM pipelines, they are often used for retrieval: selecting relevant information to include in a prompt.
        </p>
      </section>

      <section>
        <h4>Multimodal embeddings (CLIP)</h4>
        <p>
          CLIP is trained to map text and images into the same high-dimensional vector space.
          This makes it possible to compare a text embedding with an image embedding.
        </p>
        <p>
          In simple terms: if an image and a sentence describe similar content, their vectors should be close together.
        </p>
        <p>
          This is the key idea behind “multimodal” embeddings: the same type of numbers is used for different types of input.
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
          Embeddings have many dimensions (often hundreds). The pond is 2D, so we need a way to place each embedding on a flat surface.
        </p>
        <p>
          PCA (principal component analysis) reduces the high-dimensional vectors to two numbers (x and y).
          The result is an approximate layout where similar embeddings often appear closer together.
        </p>
      </section>

      <section>
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
