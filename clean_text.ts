#!/usr/bin/env -S deno run -A

async function cleanText(filePath: string) {
  try {
    // Read the content of the file
    const content = await Deno.readTextFile(filePath);

    // Define the headers and footers to be removed
    const headersAndFooters = [
      "Cien años de soledad",
      "Gabriel García Márquez"
    ];

    // Remove headers, footers, and surrounding white spaces
    let cleanedContent = content;

    // Remove Roman numerals at the start of the file
    const romanNumeralRegex = new RegExp(`^\\s*[IVXLCDM]+\\s*\\n`, "m");
    cleanedContent = cleanedContent.replace(romanNumeralRegex, "");

    headersAndFooters.forEach((text) => {
      // Replace headers and footers with a space if in the middle of a sentence
      const middleRegex = new RegExp(`(?<=\\S)\\s*${text}\\s*(?=\\S)`, "g");
      cleanedContent = cleanedContent.replace(middleRegex, "\n");

      // Replace headers and footers with a linebreak if at a sentence boundary
      const boundaryRegex = new RegExp(`(?<=\\p{P})\\s*${text}\\s*`, "gu");
      cleanedContent = cleanedContent.replace(boundaryRegex, "\n");

      // Remove headers and footers if they appear at the end of the file
      const endRegex = new RegExp(`\\s*${text}\\s*$`, "g");
      cleanedContent = cleanedContent.replace(endRegex, "");
    });

    // Remove page numbers at the beginning of a line following a complete sentence terminated with a period
    const pageNumberAfterSentenceRegex = new RegExp(`(?<=\\.)\\s*\\n\\s*\\d+\\s*\\n`, "g");
    cleanedContent = cleanedContent.replace(pageNumberAfterSentenceRegex, "\n\n");

    // Remove page numbers in the middle of a paragraph
    const pageNumberInParagraphRegex = new RegExp(`\\s*\\n\\s*\\d+\\s*\\n`, "g");
    cleanedContent = cleanedContent.replace(pageNumberInParagraphRegex, "\n");

    // Remove page numbers at the end of the file
    const pageNumberAtEndRegex = new RegExp(`\\s*\\n\\s*\\d+\\s*$`, "g");
    cleanedContent = cleanedContent.replace(pageNumberAtEndRegex, "");

    // Create the cleaned directory if it doesn't exist
    await Deno.mkdir("cleaned", { recursive: true });

    // Write the cleaned content to a new file in the cleaned directory
    const outputFilePath = `cleaned/${filePath}`;
    await Deno.writeTextFile(outputFilePath, cleanedContent);

    console.log(`Cleaned text has been written to ${outputFilePath}`);
  } catch (error) {
    console.error("Error cleaning text:", error);
  }
}

// Read the file path from command line arguments
const filePath = Deno.args[0];
if (filePath) {
  cleanText(filePath);
} else {
  console.error("Please provide a file path as an argument.");
}
