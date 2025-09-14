// --- Toggle custom coordinate fields ---
document.querySelectorAll('input[name="placement"]').forEach((el) => {
  el.addEventListener('change', function () {
    document.getElementById('customCoords').style.display =
      this.value === 'custom' ? 'block' : 'none';
  });
});

// --- Get placement coordinates based on user selection ---
function getPlacementCoordinates() {
  const placement = document.querySelector('input[name="placement"]:checked');
  if (!placement) return { x: 50, y: 700 }; // default fallback

  if (placement.value === 'invoice') return { x: 50, y: 700 };
  if (placement.value === 'remittance') return { x: 50, y: 100 };

  if (placement.value === 'custom') {
    return {
      x: parseInt(document.getElementById('xPos').value) || 0,
      y: parseInt(document.getElementById('yPos').value) || 0,
    };
  }
}

// --- Generate the endorsed PDF ---
async function generatePDF() {
  console.log("Generate PDF clicked!");

  const fileInput = document.getElementById('pdfUpload');
  const name = document.getElementById('name').value;
  const account = document.getElementById('account').value;
  const date = document.getElementById('date').value;

  if (!fileInput.files.length) {
    alert('Please upload a PDF first.');
    return;
  }

  const coords = getPlacementCoordinates();

  const endorsementText =
    `ENDORSEMENT STATEMENT\n\n` +
    `For value received, I, ${name}, hereby endorse this invoice and authorize payment from Account #${account}.\n` +
    `This endorsement confirms acceptance of services rendered and approval of the total amount due.\n\n` +
    `Signed: ${name}\n` +
    `Date: ${date}`;

  const file = fileInput.files[0];
  const arrayBuffer = await file.arrayBuffer();
  const pdfDoc = await PDFLib.PDFDocument.load(arrayBuffer);

  const pageIndex = parseInt(document.getElementById('pageNumber').value) || 0;
  const pages = pdfDoc.getPages();
  const selectedPage = pages[pageIndex] || pages[0];

  const { height } = selectedPage.getSize();
  const pdfX = coords.x;
  const pdfY = height - coords.y; // flip Y from top-left to bottom-left

  const font = await pdfDoc.embedFont(PDFLib.StandardFonts.Helvetica);

  selectedPage.drawText(endorsementText, {
    x: pdfX,
    y: pdfY,
    size: 10,
    font,
    color: PDFLib.rgb(0, 0, 0),
    lineHeight: 12
  });

  const pdfBytes = await pdfDoc.save();
  const blob = new Blob([pdfBytes], { type: 'application/pdf' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = 'endorsed_invoice.pdf';
  link.click();
}

// --- Preview and click-to-place logic ---
const previewCanvas = document.getElementById('previewCanvas');
const renderBtn = document.getElementById('renderPreview');

let lastScale = 1;
let lastPdfHeight = 0;

renderBtn.addEventListener('click', async () => {
  const fileInput = document.getElementById('pdfUpload');
  const pageIndex = parseInt(document.getElementById('pageNumber').value) || 0;
  if (!fileInput.files.length) {
    alert('Upload a PDF first.');
    return;
  }

  const file = fileInput.files[0];
  const arrayBuffer = await file.arrayBuffer();

  const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
  const totalPages = pdf.numPages;

  if (pageIndex < 0 || pageIndex >= totalPages) {
    alert(`Invalid page number. PDF has ${totalPages} page(s).`);
    return;
  }

  const page = await pdf.getPage(pageIndex + 1); // PDF.js uses 1-based indexing

  const viewport = page.getViewport({ scale: 1 });
  const desiredWidth = 800;
  const scale = desiredWidth / viewport.width;
  const scaledViewport = page.getViewport({ scale });

  const ctx = previewCanvas.getContext('2d');
  previewCanvas.width = Math.floor(scaledViewport.width);
  previewCanvas.height = Math.floor(scaledViewport.height);
  await page.render({ canvasContext: ctx, viewport: scaledViewport }).promise;

  lastScale = scale;
  lastPdfHeight = viewport.height;
});

// --- Click-to-place: convert canvas click to PDF coordinates ---
console.log("Canvas clicked!");
previewCanvas.addEventListener('click', (e) => {
  const rect = previewCanvas.getBoundingClientRect();
  const clickX = e.clientX - rect.left;
  const clickY = e.clientY - rect.top;

  const pdfX = clickX / lastScale;
  const pdfY_fromTop = clickY / lastScale;

  document.querySelector('input[value="custom"]').checked = true;
  document.getElementById('customCoords').style.display = 'block';
  document.getElementById('xPos').value = Math.round(pdfX);
  document.getElementById('yPos').value = Math.round(pdfY_fromTop); // UI shows Y from top
});