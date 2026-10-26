(() => {
  const commands = [
    ["bold", "Bold", "B"],
    ["italic", "Italic", "I"],
    ["underline", "Underline", "U"],
    ["formatBlock|<h2>", "Heading", "H2"],
    ["formatBlock|<p>", "Paragraph", "P"],
    ["insertUnorderedList", "Bulleted list", "• List"],
    ["insertOrderedList", "Numbered list", "1. List"],
    ["formatBlock|<blockquote>", "Quote", "Quote"],
    ["createLink", "Insert link", "Link"],
  ];

  function initializeEditor(textarea) {
    const wrapper = document.createElement("div");
    wrapper.className = "rich-text-editor";
    const toolbar = document.createElement("div");
    toolbar.className = "rich-text-toolbar";
    toolbar.setAttribute("role", "toolbar");
    toolbar.setAttribute("aria-label", "Text formatting");

    const editor = document.createElement("div");
    editor.className = "rich-text-canvas";
    editor.contentEditable = "true";
    editor.setAttribute("role", "textbox");
    editor.setAttribute("aria-label", "Post body rich text editor");
    editor.setAttribute("aria-multiline", "true");
    editor.innerHTML = textarea.value;

    const uploadStatus = document.createElement("p");
    uploadStatus.className = "rich-text-upload-status";
    uploadStatus.setAttribute("role", "status");
    uploadStatus.setAttribute("aria-live", "polite");

    function syncContent() {
      textarea.value = editor.innerHTML;
      textarea.dispatchEvent(new Event("input", { bubbles: true }));
    }

    function getCsrfToken() {
      const cookieToken = document.cookie
        .split("; ")
        .find((cookie) => cookie.startsWith("csrftoken="))
        ?.split("=")[1];
      return cookieToken || document.querySelector(
        'input[name="csrfmiddlewaretoken"]'
      )?.value;
    }

    async function uploadImage(file) {
      if (file.size > 5 * 1024 * 1024) {
        throw new Error("Images must be no larger than 5 MB.");
      }
      const csrfToken = getCsrfToken();
      if (!csrfToken) {
        throw new Error("Could not verify the upload request. Reload the page and try again.");
      }

      const formData = new FormData();
      formData.append("image", file);
      const response = await fetch("/posts/editor-images/upload/", {
        method: "POST",
        body: formData,
        credentials: "same-origin",
        headers: { "X-CSRFToken": csrfToken },
      });
      let result;
      try {
        result = await response.json();
      } catch {
        throw new Error("The image upload failed. Reload the page and try again.");
      }
      if (!response.ok) {
        throw new Error(result.error || "The image could not be uploaded.");
      }
      return result.url;
    }

    editor.addEventListener("paste", async (event) => {
      const imageFiles = Array.from(event.clipboardData?.items || [])
        .filter((item) => item.kind === "file" && item.type.startsWith("image/"))
        .map((item) => item.getAsFile())
        .filter(Boolean);
      if (!imageFiles.length) return;

      event.preventDefault();
      const selection = window.getSelection();
      const insertionRange = selection?.rangeCount ? selection.getRangeAt(0).cloneRange() : null;
      if (!insertionRange || !editor.contains(insertionRange.commonAncestorContainer)) {
        editor.focus();
        return;
      }

      uploadStatus.textContent = "Uploading image...";
      try {
        const imageUrls = await Promise.all(imageFiles.map(uploadImage));
        if (!editor.contains(insertionRange.commonAncestorContainer)) return;
        insertionRange.deleteContents();
        const fragment = document.createDocumentFragment();
        let lastImage;
        imageUrls.forEach((url, index) => {
          if (index) fragment.append(document.createTextNode(" "));
          const image = document.createElement("img");
          image.src = url;
          image.alt = "";
          fragment.append(image);
          lastImage = image;
        });
        insertionRange.insertNode(fragment);
        insertionRange.setStartAfter(lastImage);
        insertionRange.collapse(true);
        const updatedSelection = window.getSelection();
        updatedSelection.removeAllRanges();
        updatedSelection.addRange(insertionRange);
        syncContent();
        uploadStatus.textContent = "Image added to the article.";
      } catch (error) {
        uploadStatus.textContent = error instanceof Error
          ? error.message
          : "The image could not be uploaded.";
      }
    });

    commands.forEach(([command, label, text]) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "rich-text-button";
      button.textContent = text;
      button.title = label;
      button.setAttribute("aria-label", label);
      button.addEventListener("mousedown", (event) => event.preventDefault());
      button.addEventListener("click", () => {
        editor.focus();
        if (command === "createLink") {
          const url = window.prompt("Enter a link URL:", "https://");
          if (url) document.execCommand("createLink", false, url);
        } else {
          const [action, value] = command.split("|");
          document.execCommand(action, false, value || null);
        }
        syncContent();
      });
      toolbar.append(button);
    });

    editor.addEventListener("input", () => {
      syncContent();
    });
    textarea.form?.addEventListener("submit", () => {
      textarea.value = editor.innerHTML;
    });

    wrapper.append(toolbar, editor, uploadStatus);
    textarea.insertAdjacentElement("beforebegin", wrapper);
    textarea.classList.add("rich-text-source");
  }

  document.addEventListener("DOMContentLoaded", () => {
    const textarea = document.querySelector("#id_content");
    if (!textarea) return;
    document.body.classList.add("rich-text-enabled");
    initializeEditor(textarea);
  });
})();
