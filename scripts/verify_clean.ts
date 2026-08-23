#!/usr/bin/env -S deno run -A

// Verify that cleaned/ chapters are an accurate, lossless cleaning of the
// original chapter files: every removed fragment must be noise (headers,
// footers, page numbers, leading roman numeral), and the remaining body text
// must match verbatim.

const HEADERS = ["Cien años de soledad", "Gabriel García Márquez"];

function removeHeaders(content: string): string {
  let c = content;
  const romanNumeralRegex = new RegExp(`^\\s*[IVXLCDM]+\\s*\\n`, "m");
  c = c.replace(romanNumeralRegex, "");
  HEADERS.forEach((text) => {
    const middleRegex = new RegExp(`(?<=\\S)\\s*${text}\\s*(?=\\S)`, "g");
    c = c.replace(middleRegex, "\n");
    const boundaryRegex = new RegExp(`(?<=\\p{P})\\s*${text}\\s*`, "gu");
    c = c.replace(boundaryRegex, "\n");
    const endRegex = new RegExp(`\\s*${text}\\s*$`, "g");
    c = c.replace(endRegex, "");
  });
  return c;
}

function stripPageNumbers(content: string): string {
  return content
    .replace(/(?<=\.)\s*\n\s*\d+\s*\n/g, "\n\n")
    .replace(/\s*\n\s*\d+\s*\n/g, "\n")
    .replace(/\s*\n\s*\d+\s*$/g, "");
}

function reClean(content: string): string {
  return stripPageNumbers(removeHeaders(content));
}

// Content-preservation normalization: remove every exact header/footer
// occurrence, a leading roman-numeral chapter marker, and every digit-only
// line, then compare modulo whitespace.
function normalize(content: string): string {
  let c = content;
  HEADERS.forEach((text) => {
    c = c.split(text).join("");
  });
  c = c.replace(/^\s*[IVXLCDM]+\s*\n/, "");
  c = c.replace(/^\s*\d+\s*$/gm, "");
  return c.replace(/\s+/g, "");
}

const chapters = Array.from({ length: 20 }, (_, i) =>
  String(i + 1).padStart(2, "0")
);

let allOk = true;
for (const n of chapters) {
  const orig = await Deno.readTextFile(`${n}.md`);
  const cleaned = await Deno.readTextFile(`cleaned/${n}.md`);
  const rc = reClean(orig);

  const problems: string[] = [];

  // A. Reproducibility: cleaned file must equal a fresh run of the pipeline.
  if (rc !== cleaned) {
    allOk = false;
    problems.push(
      `A: 与脚本重跑结果不一致(cleaned 可能被手改或脚本已变更)`
    );
    // Locate first divergence for the report.
    for (let i = 0; i < Math.max(rc.length, cleaned.length); i++) {
      if (rc[i] !== cleaned[i]) {
        problems.push(
          `  首个差异 @${i}: 重跑="...${rc.slice(Math.max(0, i - 60), i + 60).replace(/\n/g, "\\n")}..." | 现文件="...${cleaned.slice(Math.max(0, i - 60), i + 60).replace(/\n/g, "\\n")}..."`
        );
        break;
      }
    }
  }

  // B. Content preservation: beyond known noise, texts must be identical.
  if (normalize(orig) !== normalize(cleaned)) {
    allOk = false;
    problems.push(`B: 正文内容不一致(除页码/页眉外存在差异)`);
    const a = normalize(orig);
    const b = normalize(cleaned);
    for (let i = 0; i < Math.max(a.length, b.length); i++) {
      if (a[i] !== b[i]) {
        problems.push(
          `  首个差异 @${i}: 原文="...${a.slice(Math.max(0, i - 60), i + 60)}..." | cleaned="...${b.slice(Math.max(0, i - 60), i + 60)}..."`
        );
        break;
      }
    }
  }

  // C. Leftover noise in the cleaned file.
  const leftover = cleaned.split("\n").filter((l) => /^\s*\d+\s*$/.test(l));
  if (leftover.length > 0) {
    allOk = false;
    problems.push(`C: 残留纯数字行 ${leftover.length} 条: ${leftover.slice(0, 5).join(", ")}`);
  }
  for (const h of HEADERS) {
    if (cleaned.includes(h)) {
      allOk = false;
      problems.push(`C: 残留页眉/页脚字符串 "${h}"`);
    }
  }

  // D. Audit what was removed from the original.
  const origLines = orig.split("\n");
  const removedDigits = origLines.filter((l) => /^\s*\d+\s*$/.test(l)).length;
  let removedHeaders = 0;
  for (const h of HEADERS) {
    removedHeaders += (orig.match(new RegExp(h, "g")) || []).length;
  }
  const status = problems.length === 0 ? "OK" : "FAIL";
  if (problems.length > 0) allOk = false;
  console.log(
    `ch.${n}: ${status}  (删除页码行 ${removedDigits}, 页眉/页脚出现 ${removedHeaders} 次)`
  );
  problems.forEach((p) => console.log(`  ${p}`));
}

console.log(allOk ? "\n全部 20 章校验通过" : "\n存在失败项,见上");
