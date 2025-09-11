import { useState } from "react";

export default function CommentGeneratorCard() {
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [comment, setComment] = useState("");

  const handleGenerateComment = () => {
    if (startDate && endDate) {
      const generatedComment = `Generated comment for the period from ${startDate} to ${endDate}.`;
      setComment(generatedComment);
    } else {
      setComment("Please enter both start and end dates.");
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white border rounded-lg shadow space-y-4">
      <h2 className="text-xl font-semibold text-center">Generate Comment</h2>

      <div className="space-y-2">
        <label className="block text-sm font-medium">Start Date</label>
        <input
          type="date"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
          className="w-full border rounded p-2"
        />
      </div>

      <div className="space-y-2">
        <label className="block text-sm font-medium">End Date</label>
        <input
          type="date"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
          className="w-full border rounded p-2"
        />
      </div>

      <button
        onClick={handleGenerateComment}
        className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
      >
        Generate Comment
      </button>

      {comment && (
        <div className="p-4 bg-gray-100 border rounded">
          <p>{comment}</p>
        </div>
      )}
    </div>
  );
}
