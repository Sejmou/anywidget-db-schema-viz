function formatDatatype(datatype: string): string {
    // Format nested structures with proper indentation for better readability
    let result = "";
    let indentLevel = 0;
    let i = 0;
    const indentSize = 2;

    while (i < datatype.length) {
        const char = datatype[i];
        const prevChar = i > 0 ? datatype[i - 1] : "";
        const nextChar = i < datatype.length - 1 ? datatype[i + 1] : "";

        if (char === "(" || char === "[") {
            result += char;
            // Add line break and indent if this opens a non-empty structure
            if (nextChar && nextChar !== ")" && nextChar !== "]") {
                indentLevel++;
                result += "\n" + " ".repeat(indentLevel * indentSize);
            }
        } else if (char === ")" || char === "]") {
            // Add newline and reduce indent before closing (if not empty structure)
            if (indentLevel > 0 && prevChar !== "(" && prevChar !== "[") {
                indentLevel--;
                result += "\n" + " ".repeat(indentLevel * indentSize);
            }
            result += char;
        } else if (char === ",") {
            result += char;
            // Add line break after comma if not at end of list
            if (
                nextChar &&
                nextChar !== " " &&
                nextChar !== ")" &&
                nextChar !== "]"
            ) {
                result += "\n" + " ".repeat(indentLevel * indentSize);
            } else if (nextChar === " ") {
                result += " ";
            }
        } else {
            result += char;
        }
        i++;
    }

    return result;
}

export { formatDatatype };