const BACKEND_URL = "http://127.0.0.1:8000";

export async function analyzeDeepfake(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  // Automatically route based on file type
  const response = await fetch(`${BACKEND_URL}/predict/auto`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Backend error: " + response.statusText);
  }

  return await response.json();
}
