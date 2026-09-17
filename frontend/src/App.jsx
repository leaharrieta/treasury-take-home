import { useRef, useState } from "react";
import "./App.css";


function App() {
  const [brandName, setBrandName] = useState("");
  const [classType, setClassType] = useState("");
  const [alcoholContent, setAlcoholContent] = useState("");
  const [netContents, setNetContents] = useState("");
  const [labelImage, setLabelImage] = useState(null);

  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  // Store the image preview URL
  const [imagePreview, setImagePreview] = useState("");

  // Allow the file input to be cleared
  const fileInputRef = useRef(null);


  // Store the selected image and create a preview
  function handleImageChange(event) {
    const file = event.target.files[0];

    if (!file) {
      return;
    }

    // Remove the previous preview from memory
    if (imagePreview) {
      URL.revokeObjectURL(imagePreview);
    }

    setLabelImage(file);
    setImagePreview(URL.createObjectURL(file));
  }

  // Clear the form, image, and verification results
  function handleClear() {
    setBrandName("");
    setClassType("");
    setAlcoholContent("");
    setNetContents("");
    setLabelImage(null);
    setResults(null);
    setError("");

    // Remove the image preview
    if (imagePreview) {
      URL.revokeObjectURL(imagePreview);
    }

    setImagePreview("");

    // Clear the actual file input
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  // Send the application values and label image to FastAPI
  async function handleSubmit(event) {
    event.preventDefault();

    if (!labelImage) {
      setError("Please upload a label image.");
      return;
    }

    setLoading(true);
    setError("");
    setResults(null);

    const formData = new FormData();

    formData.append("brand_name", brandName);
    formData.append("class_type", classType);
    formData.append("alcohol_content", alcoholContent);
    formData.append("net_contents", netContents);
    formData.append("label_image", labelImage);

    try {
      const response = await fetch(
        "/verify",
        {
          method: "POST",
          body: formData
        }
      );

      if (!response.ok) {
        throw new Error("Label verification failed.");
      }

      const data = await response.json();

      setResults(data);
    } catch (error) {
      setError(
        "Unable to verify the label. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }


  return (
    <div className="page">
      <main className="container">
        <header>
          <h1>Alcohol Label Verification</h1>
          <p>
            Compare application information with an uploaded
            alcohol label.
          </p>
        </header>

        <form onSubmit={handleSubmit}>
          <section className="card">
            <h2>Label Image</h2>

            <input
              ref={fileInputRef}
              type="file"
              accept=".jpg,.jpeg,.png,image/jpeg,image/png"
              onChange={handleImageChange}
              required
            />

            {labelImage && (
              <p className="file-name">
                Selected: {labelImage.name}
              </p>
            )}

            {imagePreview && (
              <div className="image-preview">
                <img
                  src={imagePreview}
                  alt="Uploaded alcohol label preview"
                />
              </div>
            )}
          </section>

          <section className="card">
            <h2>Application Information</h2>

            <label>
              Brand Name
              <input
                type="text"
                value={brandName}
                onChange={(event) =>
                  setBrandName(event.target.value)
                }
                required
              />
            </label>

            <label>
              Class / Type
              <input
                type="text"
                value={classType}
                onChange={(event) =>
                  setClassType(event.target.value)
                }
                required
              />
            </label>

            <label>
              Alcohol Content
              <input
                type="text"
                placeholder="Example: 45%"
                value={alcoholContent}
                onChange={(event) =>
                  setAlcoholContent(event.target.value)
                }
                required
              />
            </label>

            <label>
              Net Contents
              <input
                type="text"
                placeholder="Example: 750 mL"
                value={netContents}
                onChange={(event) =>
                  setNetContents(event.target.value)
                }
                required
              />
            </label>
          </section>

          {error && (
            <p className="error-message">
              {error}
            </p>
          )}

          <div className="button-row">
            <button
              className="verify-button"
              type="submit"
              disabled={loading}
            >
              {loading ? "Verifying..." : "Verify Label"}
            </button>

            <button
              className="clear-button"
              type="button"
              onClick={handleClear}
              disabled={loading}
            >
              Start Over
            </button>
          </div>

        </form>

        {results && (
          <section className="card results">
            <h2>Verification Results</h2>

            <div
              className={`overall ${results.overall_status}`}
            >
              Overall:{" "}
              {results.overall_status
                .replace("_", " ")
                .toUpperCase()}
            </div>

            {Object.entries(results.results).map(
              ([field, result]) => (
                <div
                  className={`result-row ${result.status}`}
                  key={field}
                >
                  <div>
                    <strong>
                      {field
                        .replaceAll("_", " ")
                        .replace(/\b\w/g, (letter) =>
                          letter.toUpperCase()
                        )}
                    </strong>

                    <p>{result.message}</p>
                  </div>

                  <span className="status">
                    {result.status
                      .replace("_", " ")
                      .toUpperCase()}
                  </span>
                </div>
              )
            )}

            <p className="processing-time">
              Processed in{" "}
              {results.processing_time_seconds} seconds
            </p>
          </section>
        )}
      </main>
    </div>
  );
}


export default App;