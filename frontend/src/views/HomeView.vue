<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import {
  AppstoreOutlined,
  PictureOutlined,
  VideoCameraOutlined,
} from "@ant-design/icons-vue";
import { useRouter } from "vue-router";
import { getGenerationModels } from "@/api/config";
import { resolveImageUrl } from "@/api/images";
import { getTemplateDetail, listTemplates } from "@/api/templates";
import TemplateDetailDialog from "@/components/templates/TemplateDetailDialog.vue";
import type { CreativeTemplate, GenerationModelOption } from "@/types";

const router = useRouter();
const showcaseItems = ref<CreativeTemplate[]>([]);
const loadingShowcase = ref(true);
const generationModels = ref<GenerationModelOption[]>([]);
const detailOpen = ref(false);
const detailLoading = ref(false);
const detail = ref<CreativeTemplate | null>(null);
const canvasModelSourceImage = "/homepage/canvas-model-source.png";
const canvasJeansImage = "/homepage/canvas-jeans.png";
const canvasJacketImage = "/homepage/canvas-jacket.png";
const canvasResultImage = "/homepage/canvas-result.png";

const capabilityCards = [
  {
    title: "AI 生图",
    eyebrow: "Image Generation",
    desc: "快速生成海报、商品图、人物视觉和概念图，让创意方向更快落地成可用画面。",
    route: "/generate",
    action: "开始生图",
    icon: PictureOutlined,
    points: ["模版快速起步", "支持自定义提示词", "适合商业视觉产出"],
  },
  {
    title: "AI 生视频",
    eyebrow: "Video Generation",
    desc: "把静态内容延展成动态片段，适合镜头预演、短视频内容和素材表达升级。",
    route: "/video-generate",
    action: "开始生视频",
    icon: VideoCameraOutlined,
    points: ["图像延展视频", "更适合内容传播", "减少后期试错成本"],
  },
  {
    title: "无限画布",
    eyebrow: "Infinite Canvas",
    desc: "把指令、素材、生成结果和修改方向放在同一块画布中，方便长期整理、比较和迭代。",
    route: "/canvas",
    action: "进入无限画布",
    icon: AppstoreOutlined,
    points: ["集中管理灵感与结果", "支持多轮编辑上下文", "适合长期项目推进"],
  },
] as const;

const imageUseCases = [
  {
    title: "商品图",
    desc: "换背景、换衣服、生成主图",
  },
  {
    title: "电商模特",
    desc: "真人换装、姿势保持、搭配展示",
  },
  {
    title: "海报设计",
    desc: "节日海报、活动视觉、宣传图",
  },
  {
    title: "头像写真",
    desc: "证件照、职业照、风格写真",
  },
  {
    title: "室内家装",
    desc: "软装搭配、空间换风格",
  },
  {
    title: "文案配图",
    desc: "文章封面、小红书配图",
  },
  {
    title: "修图增强",
    desc: "去瑕疵、补画面、高清放大",
  },
  {
    title: "创意合成",
    desc: "多图合成、产品场景化",
  },
] as const;

const marqueeItems = computed(() => [...showcaseItems.value, ...showcaseItems.value]);

async function loadShowcase() {
  loadingShowcase.value = true;
  try {
    const res = await listTemplates(1, 12);
    showcaseItems.value = res.items.filter((item) => !!item.result_image).slice(0, 10);
  } catch {
    showcaseItems.value = [];
  } finally {
    loadingShowcase.value = false;
  }
}

async function loadModels() {
  try {
    generationModels.value = await getGenerationModels();
  } catch {
    generationModels.value = [];
  }
}

async function openDetail(id: number) {
  detailOpen.value = true;
  detailLoading.value = true;
  try {
    detail.value = await getTemplateDetail(id);
  } catch {
    detailOpen.value = false;
  } finally {
    detailLoading.value = false;
  }
}

function useTemplate() {
  if (!detail.value) return;
  localStorage.setItem(
    "generateDraftFromTemplate",
    JSON.stringify({
      model: detail.value.model,
      prompt: detail.value.prompt,
      reference_images: detail.value.reference_images,
      num_images: 1,
      size: detail.value.size,
      resolution: detail.value.resolution,
      custom_size: detail.value.custom_size,
    })
  );
  detailOpen.value = false;
  router.push("/generate");
}

onMounted(() => {
  loadModels();
  loadShowcase();
});
</script>

<template>
  <div class="home-page warm-page motion-page-enter">
    <section class="section-block showcase-shell motion-fade-up" style="--motion-delay: 0.04s">
      <div v-if="loadingShowcase" class="showcase-skeleton-row">
        <div v-for="index in 6" :key="index" class="showcase-skeleton-card">
          <div class="showcase-skeleton-media" />
          <div class="showcase-skeleton-line showcase-skeleton-line-long" />
          <div class="showcase-skeleton-line showcase-skeleton-line-short" />
        </div>
      </div>
      <div v-else-if="showcaseItems.length" class="showcase-marquee">
        <div class="showcase-track showcase-track-single">
          <div
            v-for="(item, index) in marqueeItems"
            :key="`${item.id}-${index}`"
            class="showcase-card"
            @click="openDetail(item.id)"
          >
            <img
              :src="resolveImageUrl(item.result_image_thumb || item.result_image)"
              :alt="item.prompt || '效果图'"
              loading="lazy"
            />
            <div class="showcase-card-mask">
              <div class="showcase-card-prompt">{{ item.prompt || "高质量稳定生图结果" }}</div>
            </div>
            <div class="showcase-overlay">
              <div class="showcase-overlay-text">查看详情</div>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="showcase-empty">
        <div class="showcase-empty-title">高质量效果图展示位</div>
        <div class="showcase-empty-desc">模版结果图加载后，这里会自动横向滚动展示真实效果。</div>
      </div>
    </section>

    <section class="canvas-showcase motion-fade-up" style="--motion-delay: 0.08s">
      <div class="canvas-showcase-side">
        <div class="hero-summary">
          <article v-for="item in capabilityCards" :key="item.title" class="summary-card warm-card motion-card-lift">
            <div class="summary-card-top">
              <div class="summary-icon"><component :is="item.icon" /></div>
              <div class="summary-eyebrow">{{ item.eyebrow }}</div>
            </div>
            <div class="summary-title">{{ item.title }}</div>
            <div class="summary-desc">{{ item.desc }}</div>
            <div class="summary-points">
              <span v-for="point in item.points" :key="point" class="summary-point">{{ point }}</span>
            </div>
            <a-button type="primary" class="warm-primary-btn summary-btn" size="large" @click="router.push(item.route)">
              {{ item.action }}
            </a-button>
          </article>
        </div>
      </div>

      <div class="canvas-demo-shell">
        <div class="canvas-grid-bg" />
        <svg class="canvas-flow-svg" viewBox="0 0 1000 620" preserveAspectRatio="none" aria-hidden="true">
          <path class="flow-path flow-path-left-top" d="M 250 120 C 355 130, 340 270, 448 300" />
          <path class="flow-path flow-path-left-bottom" d="M 250 400 C 365 390, 350 330, 448 300" />
          <path class="flow-path flow-path-right-top" d="M 746 190 C 690 205, 640 255, 552 300" />
          <path class="flow-path flow-path-right-bottom" d="M 746 470 C 690 430, 640 350, 552 300" />
        </svg>

        <div class="canvas-pulse canvas-pulse-center" />
        <div class="canvas-pulse canvas-pulse-left" />
        <div class="canvas-pulse canvas-pulse-right-top" />
        <div class="canvas-pulse canvas-pulse-right-bottom" />

        <article class="canvas-note-card canvas-card canvas-card-note">
          <p>将模特的上衣和裤子改为提供的白色上衣和牛仔裤，模特的姿势保持不变</p>
          <span class="canvas-mini-tag">改图指令</span>
        </article>

        <article class="canvas-media-card canvas-card canvas-card-source">
          <span class="canvas-card-label">上传</span>
          <div class="fashion-frame fashion-frame-source">
            <img class="canvas-photo canvas-photo-model" :src="canvasModelSourceImage" alt="上传的模特参考图" />
          </div>
        </article>

        <article class="canvas-media-card canvas-card canvas-card-result">
          <div class="canvas-result-badge">改图 1</div>
          <div class="fashion-frame fashion-frame-result">
            <img class="canvas-photo canvas-photo-model" :src="canvasResultImage" alt="改图结果图" />
          </div>
        </article>

        <article class="canvas-garment-card canvas-card canvas-card-jeans">
          <span class="canvas-card-label">上传</span>
          <div class="garment-shape garment-jeans">
            <img class="canvas-photo canvas-photo-garment" :src="canvasJeansImage" alt="上传的裤子参考图" />
          </div>
        </article>

        <article class="canvas-garment-card canvas-card canvas-card-jacket">
          <span class="canvas-card-label">上传</span>
          <div class="garment-shape garment-jacket">
            <img class="canvas-photo canvas-photo-garment" :src="canvasJacketImage" alt="上传的衣服参考图" />
          </div>
        </article>
      </div>
    </section>

    <section class="use-cases-section motion-fade-up" style="--motion-delay: 0.12s">
      <div class="use-cases-shell">
        <div class="use-cases-heading">
          <div class="feature-story-eyebrow">AI 生图常用场景</div>
          <h2>常见生成需求，可以直接在这里快速起步。</h2>
          <p>覆盖商品、电商、海报、写真到修图增强等高频场景，让用户一眼知道 AI 生图能解决哪些实际需求。</p>
        </div>

        <div class="use-cases-grid">
          <article v-for="item in imageUseCases" :key="item.title" class="use-case-card">
            <div class="use-case-title">{{ item.title }}</div>
            <div class="use-case-desc">{{ item.desc }}</div>
          </article>
        </div>
      </div>
    </section>

    <section class="cta-band motion-fade-up" style="--motion-delay: 0.16s">
      <div class="cta-band-copy">
        <div class="feature-story-eyebrow">从展示到创作</div>
        <h2>看完效果图，下一步就进入生成和编辑。</h2>
        <p>首页负责把能力说明白，工作台负责把结果做出来。</p>
      </div>
      <div class="cta-band-actions">
        <a-button size="large" class="hero-secondary-btn" @click="router.push('/history')">查看历史记录</a-button>
        <a-button type="primary" size="large" class="warm-primary-btn" @click="router.push('/generate')">立即去创作</a-button>
      </div>
    </section>

    <TemplateDetailDialog
      v-model:open="detailOpen"
      :loading="detailLoading"
      :detail="detail"
      :generation-models="generationModels"
      @use-template="useTemplate"
    />
  </div>
</template>

<style scoped lang="scss">
.home-page {
  display: flex;
  flex-direction: column;
  gap: 22px;
  min-height: calc(100vh - 130px);
}

.section-block {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.showcase-shell {
  padding: 8px 0 12px;
  overflow: hidden;
}

.showcase-skeleton-row {
  display: flex;
  gap: 16px;
  overflow: hidden;
}

.showcase-skeleton-card {
  width: 184px;
  flex: 0 0 auto;
  padding: 10px;
  border-radius: 18px;
  background: linear-gradient(180deg, #fffaf3, #fff4e7);
  border: 1px solid rgba(241, 210, 154, 0.5);
}

.showcase-skeleton-media,
.showcase-skeleton-line {
  position: relative;
  overflow: hidden;
  background: #f4e9d5;

  &::after {
    content: "";
    position: absolute;
    inset: 0;
    transform: translateX(-100%);
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.65), transparent);
    animation: showcase-skeleton-shimmer 1.4s ease-in-out infinite;
  }
}

.showcase-skeleton-media {
  height: 180px;
  border-radius: 14px;
  margin-bottom: 12px;
}

.showcase-skeleton-line {
  height: 10px;
  border-radius: 999px;
}

.showcase-skeleton-line-long {
  width: 88%;
  margin-bottom: 8px;
}

.showcase-skeleton-line-short {
  width: 56%;
}

.showcase-marquee {
  position: relative;
  overflow: hidden;
  padding-top: 4px;

  &::before,
  &::after {
    content: "";
    position: absolute;
    top: 0;
    bottom: 0;
    width: 72px;
    z-index: 2;
    pointer-events: none;
  }

  &::before {
    left: 0;
    background: linear-gradient(90deg, #fffaf2 0%, rgba(255, 250, 242, 0) 100%);
  }

  &::after {
    right: 0;
    background: linear-gradient(270deg, #fffaf2 0%, rgba(255, 250, 242, 0) 100%);
  }
}

.showcase-track {
  display: flex;
  gap: 16px;
  width: max-content;
}

.showcase-track-single {
  animation: showcase-scroll-left 38s linear infinite;
}

.showcase-marquee:hover .showcase-track {
  animation-play-state: paused;
}

.showcase-card {
  position: relative;
  width: 184px;
  height: 236px;
  flex: 0 0 auto;
  border-radius: 18px;
  overflow: hidden;
  background: #fff4e6;
  border: 1px solid rgba(241, 210, 154, 0.7);
  box-shadow: 0 16px 28px rgba(236, 185, 88, 0.12);
  cursor: pointer;
  transition:
    transform var(--motion-duration-hover) var(--motion-ease-enter),
    box-shadow var(--motion-duration-hover) var(--motion-ease-soft),
    border-color var(--motion-duration-hover) var(--motion-ease-soft);

  img {
    width: 100%;
    height: 100%;
    display: block;
    object-fit: cover;
    transition: transform var(--motion-duration-emphasis) var(--motion-ease-enter);
  }

  &:hover {
    transform: translateY(-6px);
    border-color: #f0c46d;
    box-shadow: 0 22px 40px rgba(236, 185, 88, 0.2);
  }

  &:hover img {
    transform: scale(1.045);
  }
}

.showcase-card-mask {
  position: absolute;
  inset: auto 0 0 0;
  padding: 14px 12px 12px;
  background: linear-gradient(180deg, rgba(53, 37, 18, 0) 0%, rgba(53, 37, 18, 0.78) 100%);
}

.showcase-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, rgba(34, 25, 14, 0.08), rgba(34, 25, 14, 0.56));
  opacity: 0;
  transition: opacity var(--motion-duration-base) var(--motion-ease-soft);

  .showcase-card:hover & {
    opacity: 1;
  }
}

.showcase-overlay-text {
  padding: 10px 18px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.92);
  color: #5d4526;
  font-size: 14px;
  font-weight: 700;
  transition: transform var(--motion-duration-swift) var(--motion-ease-soft);

  .showcase-card:hover & {
    transform: translateY(-2px);
  }
}

.showcase-card-prompt {
  color: #fff8ef;
  font-size: 12px;
  line-height: 1.55;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.showcase-empty {
  margin: 8px 26px 0;
  padding: 34px 20px;
  border-radius: 24px;
  border: 1px dashed #efd3a1;
  background: linear-gradient(180deg, #fffaf3, #fff6ea);
  text-align: center;
}

.showcase-empty-title {
  color: #5b4120;
  font-size: 18px;
  font-weight: 800;
}

.showcase-empty-desc {
  margin-top: 8px;
  color: #8a7250;
  line-height: 1.8;
}

.cta-band-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.hero-secondary-btn {
  height: 44px;
  padding-inline: 20px;
  border-radius: 14px;
  border-color: #efd2a1;
  color: #9b6110;
  background: rgba(255, 250, 242, 0.92);
}

.hero-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.canvas-showcase-side {
  display: flex;
  align-items: stretch;
}

.summary-card,
.cta-band,
.canvas-demo-shell {
  border-radius: 30px;
  border: 1px solid rgba(241, 221, 183, 0.92);
  box-shadow: 0 18px 36px rgba(236, 185, 88, 0.1);
}

.summary-card {
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-height: 100%;
  padding: 24px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(255, 245, 225, 0.88));
}

.summary-card-top {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.summary-icon {
  width: 48px;
  height: 48px;
  border-radius: 18px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #fff1cf, #ffe2a8);
  color: #ad6d0a;
  font-size: 22px;
  box-shadow: 0 12px 20px rgba(236, 185, 88, 0.14);
}

.summary-eyebrow,
.feature-story-eyebrow,
.canvas-card-label {
  color: #bf8c45;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.summary-title,
.cta-band h2 {
  margin: 0;
  color: #4f361b;
  font-weight: 800;
}

.summary-title {
  font-size: 20px;
}

.summary-desc,
.cta-band p {
  margin: 0;
  color: #7c623f;
  line-height: 1.85;
}

.summary-points {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.summary-point {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(255, 243, 214, 0.92);
  color: #9f660f;
  font-size: 13px;
  font-weight: 700;
}

.summary-btn {
  align-self: flex-start;
  margin-top: auto;
}

.use-cases-section {
  position: relative;
}

.use-cases-shell {
  display: flex;
  flex-direction: column;
  gap: 22px;
  padding: 30px;
  border-radius: 30px;
  border: 1px solid rgba(241, 221, 183, 0.92);
  background:
    radial-gradient(circle at top right, rgba(255, 223, 150, 0.16), transparent 28%),
    linear-gradient(180deg, rgba(255, 252, 246, 0.96), rgba(255, 246, 226, 0.9));
  box-shadow: 0 18px 36px rgba(236, 185, 88, 0.1);
}

.use-cases-heading {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 820px;

  h2 {
    margin: 0;
    color: #4f361b;
    font-size: clamp(22px, 2.8vw, 30px);
    line-height: 1.22;
    font-weight: 800;
  }

  p {
    margin: 0;
    color: #7c623f;
    line-height: 1.85;
  }
}

.use-cases-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.use-case-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 126px;
  padding: 20px 18px;
  border-radius: 22px;
  border: 1px solid rgba(239, 220, 180, 0.9);
  background: rgba(255, 251, 242, 0.88);
  transition:
    transform var(--motion-duration-hover) var(--motion-ease-enter),
    box-shadow var(--motion-duration-hover) var(--motion-ease-soft),
    border-color var(--motion-duration-hover) var(--motion-ease-soft);

  &:hover {
    transform: translateY(-4px);
    border-color: #f0c46d;
    box-shadow: 0 16px 28px rgba(236, 185, 88, 0.12);
  }
}

.use-case-title {
  color: #9a6511;
  font-size: 16px;
  font-weight: 800;
}

.use-case-desc {
  color: #6b5537;
  line-height: 1.8;
}

.canvas-showcase {
  display: grid;
  grid-template-columns: minmax(0, 0.86fr) minmax(630px, 1.38fr);
  gap: 24px;
  align-items: start;
}

.canvas-demo-shell {
  position: relative;
  min-height: 560px;
  overflow: hidden;
  background:
    radial-gradient(circle at center, rgba(255, 224, 151, 0.18), transparent 34%),
    linear-gradient(180deg, rgba(255, 252, 246, 0.97), rgba(255, 244, 218, 0.92));
}

.canvas-grid-bg {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(239, 209, 156, 0.28) 1px, transparent 1px),
    linear-gradient(90deg, rgba(239, 209, 156, 0.28) 1px, transparent 1px);
  background-size: 34px 34px;
}

.canvas-flow-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.flow-path {
  fill: none;
  stroke: rgba(243, 176, 37, 0.82);
  stroke-width: 3;
  stroke-linecap: round;
  stroke-dasharray: 10 10;
  animation: canvas-flow-dash 10s linear infinite;
}

.canvas-card {
  position: absolute;
  z-index: 2;
  border-radius: 28px;
  border: 1px solid rgba(241, 221, 183, 0.92);
  background: rgba(255, 255, 255, 0.82);
  box-shadow: 0 20px 38px rgba(236, 185, 88, 0.12);
  backdrop-filter: blur(12px);
}

.canvas-card-note {
  top: 26px;
  left: 26px;
  width: 250px;
  padding: 24px;

  p {
    margin: 0 0 18px;
    color: #5c4221;
    line-height: 1.85;
    font-weight: 600;
  }
}

.canvas-mini-tag,
.canvas-result-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: fit-content;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(255, 243, 214, 0.94);
  color: #996109;
  font-size: 12px;
  font-weight: 700;
}

.canvas-media-card,
.canvas-garment-card {
  padding: 14px;
}

.canvas-card-source {
  left: 26px;
  bottom: 26px;
  width: 238px;
}

.canvas-card-result {
  left: 50%;
  top: 86px;
  width: 260px;
  transform: translateX(-50%);
  padding: 14px;
  animation: canvas-result-float 5.6s ease-in-out infinite;
}

.canvas-result-badge {
  position: absolute;
  left: -38px;
  top: 40px;
}

.canvas-card-jeans {
  top: 34px;
  right: 26px;
  width: 214px;
}

.canvas-card-jacket {
  right: 26px;
  bottom: 62px;
  width: 214px;
}

.fashion-frame,
.garment-shape {
  position: relative;
  border-radius: 22px;
  background:
    linear-gradient(180deg, rgba(250, 250, 250, 0.98), rgba(242, 242, 242, 0.92));
  overflow: hidden;
}

.fashion-frame {
  height: 400px;
}

.canvas-card-source .fashion-frame {
  height: 290px;
}

.garment-shape {
  height: 204px;
}

.canvas-photo {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  display: block;
}

.canvas-photo-model {
  object-fit: cover;
  object-position: center top;
}

.canvas-photo-garment {
  object-fit: contain;
  object-position: center;
  padding: 8px;
}

.fashion-frame::before,
.garment-shape::before {
  content: "";
  position: absolute;
  inset: auto 0 0 0;
  height: 26%;
  background: linear-gradient(180deg, rgba(210, 201, 190, 0), rgba(213, 205, 196, 0.72));
}

.canvas-pulse {
  position: absolute;
  z-index: 1;
  width: 16px;
  height: 16px;
  border-radius: 999px;
  background: #ffae1f;
  box-shadow: 0 0 0 10px rgba(255, 174, 31, 0.12);
  animation: canvas-node-pulse 2.8s ease-in-out infinite;
}

.canvas-pulse-center {
  left: calc(50% - 8px);
  top: calc(50% - 10px);
}

.canvas-pulse-left {
  left: 246px;
  top: 292px;
}

.canvas-pulse-right-top {
  right: 248px;
  top: 286px;
}

.canvas-pulse-right-bottom {
  right: 248px;
  top: 356px;
}

.cta-band {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 28px 30px;
  background:
    radial-gradient(circle at left center, rgba(255, 215, 124, 0.18), transparent 28%),
    linear-gradient(180deg, rgba(255, 252, 247, 0.96), rgba(255, 246, 224, 0.9));
}

.cta-band-copy {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 760px;
}

.cta-band h2 {
  font-size: 22px;
  line-height: 1.22;
}

:global(html[data-theme="dark"]),
:global(html[data-theme="midnight"]) {
  .home-page {
    .summary-card,
    .use-cases-shell,
    .use-case-card,
    .canvas-demo-shell,
    .canvas-card,
    .cta-band,
    .hero-secondary-btn,
    .showcase-skeleton-card,
    .showcase-card,
    .showcase-empty {
      background: var(--theme-panel-bg) !important;
      border-color: var(--theme-panel-border) !important;
      box-shadow: none !important;
    }

    .summary-point,
    .canvas-mini-tag,
    .canvas-result-badge {
      background: var(--theme-panel-bg-strong) !important;
      border: 1px solid var(--theme-panel-border);
      color: var(--theme-title) !important;
    }

    .summary-title,
    .use-cases-heading h2,
    .use-case-title,
    .cta-band h2,
    .showcase-empty-title {
      color: var(--theme-title) !important;
    }

    .summary-desc,
    .use-cases-heading p,
    .use-case-desc,
    .cta-band p,
    .summary-eyebrow,
    .feature-story-eyebrow,
    .canvas-card-label,
    .showcase-empty-desc,
    .canvas-card-note p {
      color: var(--text-secondary) !important;
    }

    .summary-icon {
      background: var(--theme-accent) !important;
      color: var(--theme-accent-contrast) !important;
      box-shadow: none !important;
    }

    .canvas-grid-bg {
      opacity: 0.18;
    }

    .fashion-frame,
    .garment-shape {
      background: var(--theme-panel-bg-strong) !important;
    }

    .flow-path {
      stroke: var(--theme-accent) !important;
    }

    .canvas-pulse {
      background: var(--theme-accent) !important;
      box-shadow: 0 0 0 10px rgba(var(--theme-accent-rgb), 0.14);
    }

    .showcase-skeleton-media,
    .showcase-skeleton-line {
      background: var(--theme-panel-bg-strong) !important;
    }

    .showcase-marquee::before {
      background: linear-gradient(90deg, var(--theme-panel-bg) 0%, rgba(var(--theme-surface-strong-rgb), 0) 100%) !important;
    }

    .showcase-marquee::after {
      background: linear-gradient(270deg, var(--theme-panel-bg) 0%, rgba(var(--theme-surface-strong-rgb), 0) 100%) !important;
    }

    .showcase-card:hover {
      border-color: var(--theme-border-strong) !important;
      box-shadow: 0 10px 24px var(--theme-shadow-soft) !important;
    }

    .showcase-card-mask {
      background: linear-gradient(180deg, rgba(22, 24, 29, 0) 0%, var(--theme-overlay-heavy) 100%) !important;
    }

    .showcase-card-prompt {
      color: var(--theme-accent-contrast) !important;
    }

    .showcase-overlay {
      background: linear-gradient(180deg, var(--theme-overlay-soft), var(--theme-overlay-strong)) !important;
    }

    .showcase-overlay-text {
      background: rgba(var(--theme-surface-strong-rgb), 0.96) !important;
      color: var(--theme-accent-text-hover) !important;
      border: 1px solid var(--theme-panel-border);
    }
  }
}

@keyframes showcase-scroll-left {
  from {
    transform: translate3d(0, 0, 0);
  }
  to {
    transform: translate3d(calc(-50% - 8px), 0, 0);
  }
}

@keyframes showcase-skeleton-shimmer {
  to {
    transform: translateX(100%);
  }
}

@keyframes canvas-flow-dash {
  to {
    stroke-dashoffset: -220;
  }
}

@keyframes canvas-result-float {
  0%,
  100% {
    transform: translateX(-50%) translateY(0);
  }
  50% {
    transform: translateX(-50%) translateY(-8px);
  }
}

@keyframes canvas-node-pulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 0.9;
  }
  50% {
    transform: scale(1.14);
    opacity: 1;
  }
}

@media (max-width: 1180px) {
  .canvas-showcase {
    grid-template-columns: 1fr;
  }

  .hero-summary {
    grid-template-columns: 1fr;
  }

  .use-cases-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 960px) {
  .canvas-demo-shell {
    min-height: 760px;
  }

  .canvas-card-note {
    width: 220px;
  }

  .canvas-card-source {
    width: 210px;
  }

  .canvas-card-result {
    width: 228px;
  }

  .canvas-card-jeans,
  .canvas-card-jacket {
    width: 188px;
  }
}

@media (max-width: 820px) {
  .cta-band {
    flex-direction: column;
    align-items: flex-start;
  }

  .canvas-demo-shell {
    min-height: 940px;
  }

  .canvas-card-note {
    top: 20px;
    left: 20px;
    right: 20px;
    width: auto;
  }

  .canvas-card-result {
    top: 188px;
    left: 50%;
    width: 228px;
  }

  .canvas-card-source {
    left: 20px;
    top: 470px;
    bottom: auto;
  }

  .canvas-card-jeans {
    right: 20px;
    top: 470px;
  }

  .canvas-card-jacket {
    right: 20px;
    bottom: 24px;
  }

  .canvas-flow-svg {
    opacity: 0.84;
  }

  .canvas-pulse-left {
    left: 230px;
    top: 582px;
  }

  .canvas-pulse-right-top {
    right: 208px;
    top: 582px;
  }

  .canvas-pulse-right-bottom {
    right: 208px;
    top: 770px;
  }

  .canvas-pulse-center {
    top: 402px;
  }
}

@media (max-width: 640px) {
  .summary-card,
  .use-cases-shell,
  .cta-band {
    padding: 22px;
    border-radius: 24px;
  }

  .use-cases-grid {
    grid-template-columns: 1fr;
  }

  .canvas-demo-shell {
    min-height: 1080px;
    border-radius: 24px;
  }

  .canvas-card {
    border-radius: 22px;
  }

  .canvas-card-result {
    width: 214px;
    top: 212px;
  }

  .canvas-card-source,
  .canvas-card-jeans,
  .canvas-card-jacket {
    width: calc(50% - 28px);
  }

  .canvas-card-source {
    left: 16px;
    top: 520px;
  }

  .canvas-card-jeans {
    right: 16px;
    top: 520px;
  }

  .canvas-card-jacket {
    right: 16px;
    bottom: 16px;
  }

  .canvas-card-note {
    left: 16px;
    right: 16px;
    top: 16px;
  }

  .canvas-pulse-left {
    left: 184px;
    top: 636px;
  }

  .canvas-pulse-right-top {
    right: 170px;
    top: 636px;
  }

  .canvas-pulse-right-bottom {
    right: 170px;
    top: 882px;
  }

  .canvas-pulse-center {
    top: 440px;
  }

  .showcase-empty {
    margin-inline: 18px;
  }

  .showcase-card {
    width: 142px;
    height: 190px;
    border-radius: 16px;
  }

  .showcase-skeleton-card {
    width: 142px;
    border-radius: 16px;
  }

  .showcase-skeleton-media {
    height: 136px;
  }
}
</style>

<style lang="scss">
html[data-theme="dark"] .home-page .showcase-marquee,
html[data-theme="dark"] .home-page .showcase-skeleton-row,
html[data-theme="midnight"] .home-page .showcase-marquee,
html[data-theme="midnight"] .home-page .showcase-skeleton-row {
  background: var(--theme-page-base) !important;
}

html[data-theme="dark"] .home-page .showcase-marquee::before,
html[data-theme="midnight"] .home-page .showcase-marquee::before {
  background: linear-gradient(90deg, var(--theme-page-base) 0%, rgba(var(--theme-page-base-rgb), 0) 100%) !important;
}

html[data-theme="dark"] .home-page .showcase-marquee::after,
html[data-theme="midnight"] .home-page .showcase-marquee::after {
  background: linear-gradient(270deg, var(--theme-page-base) 0%, rgba(var(--theme-page-base-rgb), 0) 100%) !important;
}
</style>
