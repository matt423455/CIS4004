// src/App.js
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ChooseUsername from './ChooseUsername';
import StartQuiz from './StartQuiz';
<<<<<<< HEAD
import './App.css'; 
=======
>>>>>>> 38e5beae04dc13a02a15ccb63a72842ce9499498

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
