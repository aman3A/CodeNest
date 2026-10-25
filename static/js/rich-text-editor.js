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
        textarea.value = editor.innerHTML;
      });
      toolbar.append(button);
    });

    editor.addEventListener("input", () => {
      textarea.value = editor.innerHTML;
      textarea.dispatchEvent(new Event("input", { bubbles: true }));
    });
    textarea.form?.addEventListener("submit", () => {
      textarea.value = editor.innerHTML;
    });

    wrapper.append(toolbar, editor);
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
