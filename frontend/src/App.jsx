import { useState } from "react";
import "./App.css";

function App() {
  const [files, setFiles] = useState([]);
  const [cards, setCards] = useState(null);
  const [loading, setLoading] = useState(false);

  const uploadCards = async () => {
    if (!files.length) return;

    setLoading(true);
    setCards(null);

    
    const formData = new FormData();

    files.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const response = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      console.log("OCR RESULT:", result);

      setCards(result.cards || []);
    } catch (error) {
      console.log(error);
      alert("Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const downloadExcel = () => {
    window.open("http://127.0.0.1:8000/download-excel", "_blank");
  };

  return (
    <div className="app">
      {loading && (
        <div className="loadingOverlay">
          <div className="loadingModal">
            <div className="loader"></div>
            <h2>Extracting Details</h2>
            <p>Please wait while we scan your visiting card(s).</p>
          </div>
        </div>
      )}

      <div className="bgGlow glowOne"></div>
      <div className="bgGlow glowTwo"></div>

      <main className="ocrCard">
        <div className="badge">WeCanServe</div>

        <h1>Business Card Scanner</h1>

        <p className="subtitle">
          Upload clear, straight visiting card images and extract details into
          structured contact cards.
        </p>

        <label className="uploadBox">
          <input
            type="file"
            accept="image/*"
            multiple
            onChange={(e) => setFiles(Array.from(e.target.files))}
          />

          <div className="uploadIcon">📇</div>

          <h3>
            {files.length
              ? `${files.length} card(s) selected`
              : "Upload visiting cards"}
          </h3>

          <p>PNG, JPG or JPEG supported. Upload straight images only.</p>
        </label>

        {files.length > 0 && (
          <div className="fileList">
            {files.map((file, index) => (
              <span key={index}>
                Card {index + 1}: {file.name}
              </span>
            ))}
          </div>
        )}

        <button
          className="primaryBtn"
          disabled={!files.length || loading}
          onClick={uploadCards}
        >
          {loading ? "Extracting..." : "Extract Details"}
        </button>

        <section className="previewTable">
          <div className="tableHeader">
            <h2>Extracted Details</h2>
            <span>{cards ? `${cards.length} Cards` : "Preview"}</span>
          </div>

          {!cards ? (
            <div className="emptyState">
              Upload cards to see extracted name, company, phone, email,
              country and address.
            </div>
          ) : (
            <>
              <div className="multiCards">
                {cards.map((card, index) => (
                  <div className="resultCard" key={index}>
                    <div className="resultCardHeader">
                      <h3>Card {card.card_no || index + 1}</h3>
                      {/* <span>{card.source || "ocr"}</span> */}
                    </div>

                    <p>
                      <b>Name:</b> {card.name || "Not available"}
                    </p>
                    <p>
                      <b>Company:</b> {card.company || "Not available"}
                    </p>
                    <p>
                      <b>Designation:</b>{" "}
                      {card.designation || "Not available"}
                    </p>
                    <p>
                      <b>Phone:</b> {card.phone || "Not available"}
                    </p>
                    <p>
                      <b>Country:</b> {card.country || "Not available"}
                    </p>
                    <p>
                      <b>Email:</b> {card.email || "Not available"}
                    </p>
                    <p>
                      <b>Website:</b> {card.website || "Not available"}
                    </p>
                    <p>
                      <b>Address:</b> {card.address || "Not available"}
                    </p>
                  </div>
                ))}
              </div>

              <div className="downloadArea">
                <button className="downloadBtn" onClick={downloadExcel}>
                  Download Excel
                </button>
              </div>
            </>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;