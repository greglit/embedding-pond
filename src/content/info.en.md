This interactive demo was built in the **ScaDS.AI Living Lab** in Leipzig.
It shows how a model can turn **text and images** into a **common numerical representation** (an embedding). These **embeddings** can then be **compared**, even if the inputs are different types of data.

---

## Embeddings - From Data to Waterlilies

**Let's imagine a universe of meaning:** each input — a sentence, a paragraph, or an image — becomes a place in this gigantic universe of meaning. **An embedding is the "numeric address" of that place:** a long list of numbers that captures the input's essence.

The magic of embeddings is that they are **learned**. A model is trained to place inputs in this space so that **similar things end up near each other**. For example, the embedding for "apple" will be close to "banana" because they often appear in similar contexts, while "house" will be farther away since it belongs to a different category of things.

These properties make embeddings **incredibly useful** across many practical use cases. They power **semantic search** ("find items like this"), **clustering** (grouping similar examples), and **recommendation**, because proximity in the space already encodes meaningful relationships.

> ### Embeddings inside AI Chatbots
> Embeddings play a **crucial role** in the **large language models (LLMs)** that power AI chatbots — embeddings are the **internal representation** that lets models "reason" about meaning. A typical LLM pipeline **tokenizes** the input, converts tokens into **embeddings**, and feeds those vectors into the **transformer layers**. In short: embeddings are the **numeric language** the model speaks — without them the rest of the system wouldn't have anything compact and comparable to work with.

### Multimodal embeddings - CLIP

OpenAI's **CLIP** model was trained to bring **images and text** into the same universe of meaning. It learns a so-called **shared vector space** by pulling matching captions and pictures together and pushing mismatches apart. The payoff is simple: a sentence and an image that describe the same thing end up **nearby**, which makes it possible to compare embeddings from different types of data.

![CLIP encoding of text and images into shared embeddings](/blogpost/clip_embeddings.gif)

Want the deep dive? Here is OpenAI's write-up on CLIP: [openai.com/research/clip](https://openai.com/research/clip)

### Rendering the waterlilies

Now imagine these embeddings as **waterlilies on a pond**. Each waterlily represents an input — a sentence or an image — and its position on the pond reflects its embedding. Just like how similar inputs cluster together in embedding space, similar waterlilies will grow near each other on the pond.

The **waterlily shape** is also generated from the **embedding values**. In the animated GIF you can see how the lily's shape is constructed from the embedding values.

The lily's **color** is also derived from the embedding. The mapping is limited to a **pink-to-white** range.

![Embedding values forming a waterlily outline and color](/blogpost/waterlily_render.gif)

---

## Planting the waterlilies - From High-dimensional to 2D Space

Embeddings live in a space with **hundreds of dimensions** — far more than we can imagine in 2D or 3D space. To show them on a flat pond, we need a smart way to **compress** that space down to **two coordinates** without losing the overall structure.

One common option is **PCA** (principal component analysis). It finds the directions where the data varies the most and projects every embedding onto those axes. The result is a **2D sketch** of the original space: not perfect, but often good enough to **preserve neighborhoods**, so similar inputs still land near each other.

### The Modality Gap

The picture you see below is the result of the **2D projection** described above. Once we lay the embeddings out on this flat map, a characteristic pattern often appears: **text points** and **image points** drift into **different regions**. This **spatial separation** is called the **modality gap**. It means that even when a sentence and an image describe the same concept, their vectors may not end up as close as we would hope.

While it's still possible to compute meaningful similarities, the gap leads to a misleading visual impression that is also present in our waterlily pond. We tried some approaches to mitigate that, which can be explored by clicking on the **Science** button in the bottom-right corner. Feel free to experiment with the settings and see how they affect the layout!

![Modality gap visualization](/blogpost/modality_gap.jpeg)

In this graphic, the projection is done with **UMAP** rather than PCA. It is similar in spirit, but tends to make the modality gap even clearer. Learn more [here](https://biostatsquid.com/pca-umap-tsne-comparison/).

---

## Tech

Everything runs in your **browser**. There is no **server-side computation** and your inputs are not sent anywhere by this app.

Embeddings are computed with [Transformers.js](https://github.com/huggingface/transformers.js), running a [CLIP](https://openai.com/index/clip/) model locally.

Transformers.js uses browser features like **WebAssembly (WASM)** and **WebGPU/WebGL** (depending on the device) to run the model. Performance depends on your browser and hardware.

### What happens when you press "Grow"

**Text** is tokenized into integer IDs. **Images** are resized and normalized. Both are passed through **CLIP** to produce an **embedding vector**. The app then derives a **waterlily shape** and **color** from the numbers and renders the waterlily as an SVG shape.

When you press **"Plant"**, the app updates the **PCA layout** to compute positions for all waterlilies on the pond.

### Model download and caching

The first time you use the demo, the **model files** may be downloaded to your browser. After that, your browser can **cache** them so that future runs are faster.

### Data handling

The app does **not upload** your text or images. If you choose an image file, the browser creates a **local object URL** so the image can be displayed and processed on your device.

The embeddings that are produced are only kept **in memory** during the app's runtime — represented as JSON-like structures — and are not permanently stored or sent to any server.
