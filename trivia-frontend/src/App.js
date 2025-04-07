// src/App.js
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ChooseUsername from './ChooseUsername';
import StartQuiz from './StartQuiz';
import './App.css'; 

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/choose-username" element={<ChooseUsername />} />
                <Route path="/" element={<StartQuiz />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
