// src/StartQuiz.js
import React, { useState, useEffect, useRef } from 'react';
import './StartQuiz.css'; 

function StartQuiz({ username }) {
    const [userStats, setUserStats] = useState({
        high_score: '--',
        total_games: '--',
        avg_score: '--'
    });
    const [leaderboard, setLeaderboard] = useState([]);
    const [quizStarted, setQuizStarted] = useState(false);
    const [timer, setTimer] = useState(60);
    const [question, setQuestion] = useState(null);
    const [done, setDone] = useState(false);
    const [scoreData, setScoreData] = useState({
        score: 0,
        correct_count: 0,
        wrong_count: 0
    });

    const timerIdRef = useRef(null);

    // Helper function: If response is 401, redirect to /login.
    const checkAuth = async (response) => {
        if (response.status === 401) {
            window.location.href = '/login';
            throw new Error('Unauthorized');
        }
        return response;
    };

    // On mount, fetch stats
    useEffect(() => {
        fetchStats();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    // Timer logic
    useEffect(() => {
        if (quizStarted && timer > 0 && !done) {
            timerIdRef.current = setInterval(() => {
                setTimer(prev => prev - 1);
            }, 1000);
        }
        return () => clearInterval(timerIdRef.current);
    }, [quizStarted, timer, done]);

    useEffect(() => {
        if (timer <= 0 && quizStarted && !done) {
            finishQuiz();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [timer, quizStarted, done]);

    const fetchStats = async () => {
        try {
            const res = await fetch('/get_stats');
            await checkAuth(res);
            const data = await res.json();
            if (data.error) {
                console.error("Failed to get stats:", data.error);
                return;
            }
            // If username is empty, force user to choose one.
            if (!data.user_stats.username) {
                window.location.href = '/choose-username';
                return;
            }
            setUserStats(data.user_stats);
            setLeaderboard(data.leaderboard);
        } catch (err) {
            console.error("Error fetching stats:", err);
        }
    };

    const startQuiz = async () => {
        try {
            const res = await fetch('/start_quiz', { method: 'POST' });
            await checkAuth(res);
            const data = await res.json();
            console.log("Quiz started:", data);
            setQuizStarted(true);
            setTimer(60);
            setDone(false);
            setQuestion(null);
            setScoreData({ score: 0, correct_count: 0, wrong_count: 0 });
            loadQuestion();
        } catch (err) {
            console.error("Error starting quiz:", err);
        }
    };

    const loadQuestion = async () => {
        try {
            const res = await fetch('/get_question');
            await checkAuth(res);
            const qdata = await res.json();
            console.log("Got question:", qdata);
            if (qdata.done) {
                finishQuiz();
            } else {
                setQuestion(qdata);
            }
        } catch (err) {
            console.error("Error loading question:", err);
        }
    };

    const submitAnswer = async (answer) => {
        if (!question) return;
        try {
            const res = await fetch('/submit_answer', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question_id: question.question_id,
                    answer: answer
                })
            });
            await checkAuth(res);
            await res.json();
            loadQuestion();
        } catch (err) {
            console.error("Error submitting answer:", err);
        }
    };

    const finishQuiz = async () => {
        clearInterval(timerIdRef.current);
        try {
            const res = await fetch('/finish_quiz', { method: 'POST' });
            await checkAuth(res);
            const result = await res.json();
            console.log("Quiz finished:", result);
            setDone(true);
            setQuizStarted(false);
            setQuestion(null);
            setScoreData({
                score: result.score,
                correct_count: result.correct_count,
                wrong_count: result.wrong_count
            });
            fetchStats();
        } catch (err) {
            console.error("Error finishing quiz:", err);
        }
    };

    return (
        <div>
            <h1>Welcome to Trivia Paradise, {username || 'UnknownUser'}!</h1>

            {/* User Stats */}
            <div>
                <h3>Your Stats</h3>
                <p>High Score: {userStats.high_score}</p>
                <p>Total Games: {userStats.total_games}</p>
                <p>Average Score: {userStats.avg_score}</p>
            </div>
            <hr />

            {/* Leaderboard */}
            <div>
                <h3>Leaderboard</h3>
                <table border="1" cellPadding="5">
                    <thead>
                        <tr>
                            <th>Username</th>
                            <th>High Score</th>
                        </tr>
                    </thead>
                    <tbody>
                        {leaderboard.map((row, i) => (
                            <tr key={i}>
                                <td>{row.username || "Unknown"}</td>
                                <td>{row.high_score}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            <hr />

            {/* Start Button / Quiz / Results */}
            {!quizStarted && !done && (
                <button onClick={startQuiz}>Start Quiz</button>
            )}

            {quizStarted && !done && (
                <div>
                    <h2>Time Left: {timer} seconds</h2>
                    {question ? (
                        <>
                            <p>{question.question}</p>
                            <button onClick={() => submitAnswer('True')}>True</button>
                            <button onClick={() => submitAnswer('False')}>False</button>
                        </>
                    ) : (
                        <p>Loading question...</p>
                    )}
                </div>
            )}

            {done && (
                <div>
                    <h2>Quiz Results</h2>
                    <p>Final Score: {scoreData.score}</p>
                    <p>Correct: {scoreData.correct_count}</p>
                    <p>Wrong: {scoreData.wrong_count}</p>
                    <button onClick={startQuiz}>Play Again</button>
                </div>
            )}
        </div>
    );
}

export default StartQuiz;
