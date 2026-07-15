export const VIDEO_GENERATE_DRAFT_KEY = "videoGenerateDraft";

export interface VideoGenerateDraftPayload {
  mode: "imageToVideo";
  prompt?: string;
  reference_images: string[];
}

export function saveImageToVideoDraft(payload: {
  referenceImage: string;
  prompt?: string;
}) {
  const referenceImage = String(payload.referenceImage || "").trim();
  if (!referenceImage) return false;
  const draft: VideoGenerateDraftPayload = {
    mode: "imageToVideo",
    prompt: String(payload.prompt || "").trim(),
    reference_images: [referenceImage],
  };
  localStorage.setItem(VIDEO_GENERATE_DRAFT_KEY, JSON.stringify(draft));
  return true;
}

export function consumeVideoGenerateDraft(): VideoGenerateDraftPayload | null {
  const raw = localStorage.getItem(VIDEO_GENERATE_DRAFT_KEY);
  if (!raw) return null;
  try {
    const draft = JSON.parse(raw) as VideoGenerateDraftPayload;
    const referenceImages = Array.isArray(draft.reference_images)
      ? draft.reference_images.map((item) => String(item || "").trim()).filter(Boolean)
      : [];
    if (!referenceImages.length) {
      localStorage.removeItem(VIDEO_GENERATE_DRAFT_KEY);
      return null;
    }
    localStorage.removeItem(VIDEO_GENERATE_DRAFT_KEY);
    return {
      mode: "imageToVideo",
      prompt: String(draft.prompt || "").trim(),
      reference_images: referenceImages,
    };
  } catch {
    localStorage.removeItem(VIDEO_GENERATE_DRAFT_KEY);
    return null;
  }
}
