<template>
  <div class="info-popover" role="dialog" aria-modal="false" aria-label="Information">
    <header>
      <h2>Info - Behind the Embedding Pond</h2>
      <IconButton label="Close" @click="emit('close')" />
    </header>

    <div class="info-popover__body">
      <section>
        <p>
          This interactive demo was built in the <strong>ScaDS.AI Living Lab</strong> in Leipzig.
          It shows how a model can turn <strong>text and images</strong> into a <strong>common numerical representation</strong> (an
          embedding). These <strong>embeddings</strong> can then be <strong>compared</strong>, even if the inputs are different types of data.
        </p>
      </section>

      <section class="top-separator">
        <h3>Embeddings - From Data to Waterlilies</h3>
        <p>
          <strong>Let's imagine a universe of meaning:</strong> each input — a sentence, a paragraph, or an image — becomes 
          a place in this gigantic universe of meaning. <strong>An embedding is the "numeric address" of that place:</strong> 
          a long list of numbers that captures the input's essence.
        </p>
        <p>
          The magic of embeddings is that they are <strong>learned</strong>. A model is trained to place inputs in this space so that
          <strong>similar things end up near each other</strong>. For example, the embedding for "apple" will be close to "banana" because they
          often appear in similar contexts, while "house" will be farther away since it belongs to a different category of things.
        </p>
        <p>
          These properties make embeddings <strong>incredibly useful</strong> across many practical use cases. They power
          <strong>semantic search</strong> ("find items like this"), <strong>clustering</strong> (grouping similar examples), and
          <strong>recommendation</strong>, because proximity in the space already encodes meaningful relationships.
        </p>
        <div class="info-popover__callout">
          <h5>
            <i class="fa-solid fa-circle-info"></i>
            Embeddings inside AI Chatbots
          </h5>
          <p>
            Embeddings play a <strong>crucial role</strong> in the <strong>large language models (LLMs)</strong> that power AI chatbots — embeddings are the <strong>internal representation</strong>
            that lets models "reason" about meaning. A typical LLM pipeline <strong>tokenizes</strong> the input, converts tokens into
            <strong>embeddings</strong>, and feeds those vectors into the <strong>transformer layers</strong>. In short: embeddings are the
            <strong>numeric language</strong> the model speaks — without them the rest of the system wouldn't have anything compact and
            comparable to work with.
          </p>
        </div>
        <h5>Multimodal embeddings — CLIP</h5>
        <p>
          OpenAI's <strong>CLIP</strong> model was trained to bring <strong>images and text</strong> into the same universe of meaning. It learns a
          so called <strong>shared vector space</strong> by pulling matching captions and pictures together and pushing mismatches apart. The payoff is
          simple: a sentence and an image that describe the same thing end up <strong>nearby</strong>, which makes it possible to compare embeddings from different
          types of data.
        </p>
        <img
          class="info-popover__gif"
          src="/blogpost/clip_embeddings.gif"
          alt="CLIP encoding of text and images into shared embeddings"
          loading="lazy"
        />
        <p style="margin-top: 20px;">
          Want the deep dive? Here is OpenAI's writeup on CLIP:
          <a href="https://openai.com/research/clip" target="_blank" rel="noreferrer">openai.com/research/clip</a>
        </p>
      </section>

      <section>
        <h5>Rendering the waterlilies</h5>
        <p>
          <!-- now transfer to lilypond: map = pond, points = waterlilies, embeddingvalues = shape and color of the lily analog to first paragraph -->
          Now imagine these embeddings as <strong>waterlilies on a pond</strong>. Each waterlily represents an input — a sentence or an image — and its position on the pond reflects its embedding.
          Just like how similar inputs cluster together in embedding space, similar waterlilies will grow near each other on the pond.
        </p>
        <p>
          The <strong>waterlily shape</strong> is also generated from the <strong>embedding values</strong>. In the animated GIF you can see how the lily's shape is constructed from the embedding values.
        </p>
        <p>
          The lily's <strong>color</strong> is also derived from the embedding. The mapping is limited to a <strong>pink‑to‑white</strong> range.
        </p>
        <img
          class="info-popover__gif"
          src="/blogpost/waterlily_render.gif"
          alt="Embedding values forming a waterlily outline and color"
          loading="lazy"
        />
      </section>

      <section class="top-separator">
        <h3>Planting the waterlilies — From Highdimensional to 2D Space</h3>
        <p>
          Embeddings live in a space with <strong>hundreds of dimensions</strong> — far more than we can imagine in 2D or 3D space. To show them on a flat pond,
          we need a smart way to <strong>compress</strong> that space down to <strong>two coordinates</strong> without losing the overall
          structure.
        </p>
        <p>
          One common option is <strong>PCA</strong> (principal component analysis). It finds the directions where the data varies the most
          and projects every embedding onto those axes. The result is a <strong>2D sketch</strong> of the original space: not perfect, but
          often good enough to <strong>preserve neighborhoods</strong>, so similar inputs still land near each other.
        </p>

        <h5>The Modality Gap</h5>
        <p>
          The picture you see below is the result of the <strong>2D projection</strong> described above. Once we lay the embeddings out on
          this flat map, a characteristic pattern often appears: <strong>text points</strong> and <strong>image points</strong> drift into
          <strong>different regions.</strong> This <strong>spatial separation</strong> is called the <strong>modality gap</strong>. It means that even when a sentence and an image describe the
          same concept, their vectors may not end up as close as we would hope. 
        </p>
        <p>
          While it's still possible to compute meaningful similarities, 
          the gap leads to a misleading visual impression that is also present in our waterlily pond. We tried some approaches to mitigate that, 
          which can be explored by clicking on the <strong>Science</strong> button   in the bottom right corner. Feel free to experiment with the settings and see how they affect the layout!
        </p>
        <figure style="margin:10px 0 0;">
          <img src="/blogpost/modality_gap.jpeg" alt="Modality gap visualization" style="max-width:100%; border-radius:8px;" />
          <figcaption style="font-size:0.85rem; color:rgba(29,41,51,0.66); margin-top:6px;">
            Image Source: https://medium.com/@zilliz_learn/from-clip-to-jinaclip-general-text-image-representation-learning-for-search-and-multimodal-rag-4bdacb74cc80
          </figcaption>
        </figure>
        <p>
          In this graphic the projection is done with <strong>UMAP</strong> rather than PCA. It is similar in spirit, but tends to make the
          modality gap even clearer. Learn more
          <a href="https://biostatsquid.com/pca-umap-tsne-comparison/" target="_blank" rel="noreferrer">here</a>.
        </p>
      </section>
      <section class="top-separator">
        <h3>Tech</h3>
        <p>
          Everything runs in your <strong>browser</strong>. There is no <strong>server‑side computation</strong> and your inputs are not sent
          anywhere by this app.
        </p>
        <p>
          Embeddings are computed with
          <a href="https://github.com/huggingface/transformers.js" target="_blank" rel="noreferrer">Transformers.js</a>, running a
          <a href="https://openai.com/index/clip/" target="_blank" rel="noreferrer">CLIP</a> model locally.
        </p>
        <p>
          Transformer.js uses browser features like <strong>WebAssembly (WASM)</strong> and <strong>WebGPU/WebGL</strong> (depending on the
          device) to run the model. Performance depends on your browser and hardware.
        </p>
        <h5>What happens when you press “Grow”</h5>
        <p>
          <strong>Text</strong> is tokenized into integer IDs. <strong>Images</strong> are resized and normalized.
          Both are passed through <strong>CLIP</strong> to produce an <strong>embedding vector</strong>.
          The app then derives a <strong>waterlily shape</strong> and <strong>color</strong> from the numbers and renders the waterlily as an SVG
          shape.
        </p>
        <p>
          When you press <strong>“Plant”</strong>, the app updates the <strong>PCA layout</strong> to compute positions for all waterlilies on
          the pond.
        </p>
        <h5>Model download and caching</h5>
        <p>
          The first time you use the demo, the <strong>model files</strong> may be downloaded to your browser.
          After that, your browser can <strong>cache</strong> them so that future runs are faster.
        </p>
        <h5>Data handling</h5>
        <p>
          The app does <strong>not upload</strong> your text or images.
          If you choose an image file, the browser creates a <strong>local object URL</strong> so the image can be displayed and processed on
          your device.
        </p>
        <p>
          The embeddings that are produced are only kept <strong>in memory</strong> during the app's runtime — represented as JSON‑like
          structures — and are not permanently stored or sent to any server.
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

.info-popover__callout {
  margin: 16px 0;
  padding: 12px 14px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  border-radius: 10px;
  background: rgba(248, 250, 252, 0.7);
}

.info-popover__callout h5 {
  margin: 0 0 8px;
  font-size: 0.95rem;
  color: rgba(29, 41, 51, 0.7);
  text-align: left;
}

.info-popover__callout p {
  margin: 0;
}
</style>
