const documentList = document.querySelector("#document-list");
const fileInput = document.querySelector("#file-input");
const dropZone = document.querySelector("#drop-zone");
const uploadStatus = document.querySelector("#upload-status");
const refreshButton = document.querySelector("#refresh-documents");
const messages = document.querySelector("#messages");
const chatForm = document.querySelector("#chat-form");
const questionInput = document.querySelector("#question-input");
const sendButton = document.querySelector("#send-button");

function setStatus(message) {
  uploadStatus.textContent = message;
}

function escapeText(value) {
  const element = document.createElement("span");
  element.textContent = value;
  return element.innerHTML;
}

function appendMessage(role, text, sources = []) {
  const article = document.createElement("article");
  article.className = `message ${role}`;

  const body = document.createElement("div");
  body.className = "message-body";
  body.textContent = text;

  if (sources.length > 0) {
    const sourceBox = document.createElement("div");
    sourceBox.className = "sources";
    sourceBox.textContent = "Sources:";
    for (const source of sources) {
      const item = document.createElement("span");
      item.textContent = source;
      sourceBox.appendChild(item);
    }
    body.appendChild(sourceBox);
  }

  article.appendChild(body);
  messages.appendChild(article);
  messages.scrollTop = messages.scrollHeight;
  return article;
}

function renderDocuments(documents) {
  documentList.innerHTML = "";

  if (documents.length === 0) {
    const item = document.createElement("li");
    item.className = "document-item";
    item.innerHTML = '<div><div class="document-name">No documents indexed</div></div>';
    documentList.appendChild(item);
    return;
  }

  for (const documentRecord of documents) {
    const item = document.createElement("li");
    item.className = "document-item";
    item.innerHTML = `
      <div>
        <div class="document-name">${escapeText(documentRecord.filename)}</div>
        <div class="document-meta">${documentRecord.chunks} chunks</div>
      </div>
      <button class="document-delete" type="button" data-id="${escapeText(documentRecord.id)}">Delete</button>
    `;
    documentList.appendChild(item);
  }
}

async function loadDocuments() {
  const response = await fetch("/api/documents");
  if (!response.ok) {
    throw new Error(`Failed to load documents: ${response.status}`);
  }
  renderDocuments(await response.json());
}

async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  setStatus(`Uploading ${file.name}...`);
  const response = await fetch("/api/documents", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `Upload failed: ${response.status}`);
  }

  const result = await response.json();
  setStatus(`Indexed ${result.filename} (${result.chunks} chunks).`);
}

async function uploadFiles(files) {
  for (const file of files) {
    await uploadDocument(file);
  }
  await loadDocuments();
}

async function deleteDocument(id) {
  const response = await fetch(`/api/documents/${encodeURIComponent(id)}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error(`Delete failed: ${response.status}`);
  }
  await loadDocuments();
}

async function sendQuery(question) {
  sendButton.disabled = true;
  const pending = appendMessage("assistant", "Thinking...");

  try {
    const response = await fetch("/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `Query failed: ${response.status}`);
    }
    const result = await response.json();
    pending.remove();
    appendMessage("assistant", result.answer, result.sources || []);
  } finally {
    sendButton.disabled = false;
    questionInput.focus();
  }
}

fileInput.addEventListener("change", async () => {
  try {
    await uploadFiles([...fileInput.files]);
  } catch (error) {
    setStatus(error.message);
  } finally {
    fileInput.value = "";
  }
});

dropZone.addEventListener("dragover", (event) => {
  event.preventDefault();
  dropZone.classList.add("dragging");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("dragging");
});

dropZone.addEventListener("drop", async (event) => {
  event.preventDefault();
  dropZone.classList.remove("dragging");
  try {
    await uploadFiles([...event.dataTransfer.files]);
  } catch (error) {
    setStatus(error.message);
  }
});

refreshButton.addEventListener("click", async () => {
  try {
    await loadDocuments();
  } catch (error) {
    setStatus(error.message);
  }
});

documentList.addEventListener("click", async (event) => {
  const button = event.target.closest(".document-delete");
  if (!button) {
    return;
  }
  try {
    await deleteDocument(button.dataset.id);
    setStatus("Document deleted.");
  } catch (error) {
    setStatus(error.message);
  }
});

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!question) {
    return;
  }

  appendMessage("user", question);
  questionInput.value = "";

  try {
    await sendQuery(question);
  } catch (error) {
    appendMessage("assistant", error.message);
  }
});

questionInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    chatForm.requestSubmit();
  }
});

loadDocuments().catch((error) => setStatus(error.message));
