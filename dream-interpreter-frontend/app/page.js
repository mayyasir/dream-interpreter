"use client";
import { useState, useEffect } from "react";
import axios from "axios";

export default function Home() {
  const [dreamText, setDreamText] = useState("");
  const [interpretation, setInterpretation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dreamHistory, setDreamHistory] = useState([]);

  // Function to analyze a new dream
  const analyzeDream = async () => {
    setLoading(true);
    setInterpretation(null);

    try {
      const response = await axios.post("http://localhost:8000/analyze_dream", {
        dream_text: dreamText,
      });

      setInterpretation(response.data);
      // Refresh history after submitting a new dream
      getDreamHistory();
    } catch (error) {
      console.error("Error analyzing dream:", error);
      setInterpretation({ error: "Failed to fetch interpretation. Try again." });
    }

    setLoading(false);
  };

  // Function to fetch dream history
  const getDreamHistory = async () => {
    try {
      const response = await axios.get("http://localhost:8000/dream_history");
      setDreamHistory(response.data.reverse()); // Show latest dreams first
    } catch (error) {
      console.error("Error fetching dream history:", error);
    }
  };

  // Fetch history on initial load
  useEffect(() => {
    getDreamHistory();
  }, []);

  return (
    <div className="min-h-screen flex flex-col items-center bg-gray-50 p-8">
      {/* Title at the very top */}
      <h1 className="text-4xl font-bold text-black mt-6">AI Dream Interpreter</h1>

      {/* Button to fetch history */}
      <button
        className="mt-4 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg shadow-md transition-all"
        onClick={getDreamHistory}
      >
        Refresh Dream History
      </button>

      {/* Dream History Section */}
      {dreamHistory.length > 0 && (
        <div className="mt-6 p-5 bg-white border border-gray-300 rounded-lg shadow-md w-full max-w-lg">
          <h2 className="text-xl font-semibold text-black mb-2">Past Dreams</h2>
          <div className="max-h-60 overflow-y-auto">
            {dreamHistory.map((dream, index) => (
              <div key={index} className="border-b border-gray-200 py-3">
                <p className="text-gray-700">
                  <strong className="text-black">Dream:</strong> {dream.dream_text}
                </p>
                <p className="text-gray-700">
                  <strong className="text-black">Interpretation:</strong> {dream.interpretation}
                </p>
                <p className="text-gray-700">
                  <strong className="text-black">Emotion:</strong> {dream.emotion}
                </p>
                <p className="text-gray-700">
                  <strong className="text-black">Confidence:</strong> {dream.confidence.toFixed(2)}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Interpretation Box above input field */}
      {interpretation && (
        <div className="mt-6 p-5 bg-white border border-gray-300 rounded-lg shadow-md w-full max-w-lg">
          {interpretation.error ? (
            <p className="text-red-500">{interpretation.error}</p>
          ) : (
            <>
              <h2 className="text-xl font-semibold text-black">Interpretation:</h2>
              <p className="mt-2 text-black">{interpretation.interpretation}</p>
              <h3 className="mt-4 text-lg font-semibold text-black">Emotion: {interpretation.emotion}</h3>
              <p className="text-gray-700">Confidence: {interpretation.confidence.toFixed(2)}</p>
            </>
          )}
        </div>
      )}

      {/* Input Box moved slightly below middle */}
      <textarea
        className="w-full max-w-lg mt-10 p-4 border-2 border-black rounded-lg shadow-sm focus:outline-none text-black bg-white"
        rows="4"
        placeholder="Describe your dream here..."
        value={dreamText}
        onChange={(e) => setDreamText(e.target.value)}
      />

      {/* Button placed further below for better spacing */}
      <button
        className="mt-6 bg-green-700 hover:bg-green-800 text-white font-bold py-3 px-6 rounded-lg shadow-md transition-all"
        onClick={analyzeDream}
        disabled={loading}
      >
        {loading ? "Interpreting..." : "Interpret Dream"}
      </button>
    </div>
  );
}