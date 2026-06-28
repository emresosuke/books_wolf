// Bu kodu tarayıcınızın konsoluna (F12 -> Console) yapıştırın ve Enter'a basın.
// Çıkan sonucu kopyalayıp bana gönderin.

const inputs = Array.from(document.querySelectorAll('input, select, textarea'));
const fields = inputs.map(input => {
    return {
        tag: input.tagName,
        type: input.type,
        id: input.id,
        name: input.name,
        placeholder: input.placeholder,
        className: input.className
    };
});

console.log(JSON.stringify(fields, null, 2));
