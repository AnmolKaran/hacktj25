import { useState } from 'react';

function Realtime() {
  const [inputValue, setInputValue] = useState('');
  const [chips, setChips] = useState([]);

  const handleChange = (event) => {
    setInputValue(event.target.value);
  };

  const handleKeyDown = (event) => {
    if (event.key === ' ' || event.key === 'Enter') {
      event.preventDefault();
      if (inputValue.trim() && !chips.includes(inputValue.trim())) {
        setChips([...chips, inputValue.trim()]);
        setInputValue('');
      }
    }
  };

  const removeChip = (chipToRemove) => {
    setChips(chips.filter(chip => chip !== chipToRemove));
  };

  const handleSubmit = () => {
    const chipsJSON = JSON.stringify(chips);
    console.log(chipsJSON);
  };

  return (
    <>
      <div className="flex justify-center items-center h-screen bg-gradient-to-r from-blue-500 to-teal-400">
        <div className="w-full max-w-lg p-8 bg-white rounded-xl shadow-xl">
          <h1 className="text-3xl font-bold text-center text-gray-800 mb-6">Real Time</h1>
          <div className="flex items-center space-x-4 mb-4">
            <input
              type="text"
              value={inputValue}
              onChange={handleChange}
              onKeyDown={handleKeyDown}
              className="border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 px-4 py-2 rounded-md w-full"
              placeholder="Type a word and hit space"
            />
            <button
              onClick={handleSubmit}
              className="bg-blue-700 text-white px-6 py-2 rounded-md hover:bg-blue-800 transition duration-200"
            >
              Submit
            </button>
          </div>
          <div className="flex flex-wrap space-x-2 mb-6">
            {chips.map((chip, index) => (
              <div key={index} className="bg-blue-100 text-blue-700 px-4 py-2 rounded-full flex items-center">
                <span>{chip}</span>
                <button
                  onClick={() => removeChip(chip)}
                  className="ml-2 text-red-500 hover:text-red-700 transition duration-150"
                >
                  X
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}

export default Realtime;
