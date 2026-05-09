export async function analyzeDeepfake(formData: FormData, file: File) {
  let endpoint = "";

  const imageTypes = ["image/jpeg", "image/png", "image/webp", "image/jpg"];
  const videoTypes = ["video/mp4", "video/mkv", "video/avi", "video/webm"];

  if (imageTypes.includes(file.type)) {
    endpoint = "/predict/image";
  } else if (videoTypes.includes(file.type)) {
    endpoint = "/predict/video";
  } else {
    throw new Error("Unsupported file type");
  }

  const response = await fetch(`http://localhost:8000${endpoint}`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Backend Error");
  }

  return await response.json();
}
