// src/ChooseUsername.js
import React, { useState } from 'react';

function ChooseUsername({ onUsernameSet }) {
    const [username, setUsername] = useState('');

    // Helper: If response is unauthorized, redirect to login
    const checkAuth = async (response) => {
        if (response.status === 401) {
            window.location.href = '/login';
            throw new Error('Unauthorized');
        }
        return response;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!username.trim()) {
            alert("Username cannot be blank!");
            return;
        }

        try {
            const formData = new FormData();
            formData.append('username', username);
            const res = await fetch('/set_username', {
                method: 'POST',
                body: formData
            });
            await checkAuth(res);
            if (!res.ok) {
                const text = await res.text();
                alert("Error setting username: " + text);
                return;
            }
            // Call onUsernameSet if provided, then redirect to home
            if (onUsernameSet) onUsernameSet(username);
            window.location.href = '/';
        } catch (err) {
            console.error("Error submitting username:", err);
        }
    };

    return (
        <div>
            <h1>Pick a Username</h1>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    name="username"
                    placeholder="Enter your username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                />
                <button type="submit">Submit</button>
            </form>
        </div>
    );
}

export default ChooseUsername;
