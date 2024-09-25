import React, { useState } from 'react';
import axios from 'axios'; // npm install axios

function App() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [messages, setMessages] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!email || !password) {
      setMessages([...messages, 'Email and Password are required']);
    } else {
      try {
        const response = await axios.post('/api/login', { email, password });
        if (response.data.success) {
          setMessages([...messages, 'Login successful!']);
          // 여기서 페이지 리다이렉션 또는 다른 후속 동작 처리
        } else {
          setMessages([...messages, 'Login failed. Please check your credentials.']);
        }
      } catch (error) {
        setMessages([...messages, 'An error occurred. Please try again.']);
      }
    }
  };

  return (
    <div className="is-preload">
      {/* Header */}
      <header id="header">
        <h1><a href="/">AutoAngle</a></h1>
        <a href="#menu">Menu</a>
      </header>

      {/* Menu */}
      <nav id="menu">
        <ul className="links">
          <li><a href="/">Home</a></li>
          <li><a href="/info">Usage Information</a></li>
          <li><a href="/article">Related Article</a></li>
        </ul>
        <ul className="actions stacked">
          <li><a href="/register" className="button primary fit">Sign Up</a></li>
          <li><a href="/login" className="button fit">Log In</a></li>
        </ul>
      </nav>

      {/* Main Section */}
      <section id="main" className="wrapper">
        <header>
          <h2>Login</h2>
          <p>Lorem justo in tellus aenean lacinia felis.</p>
        </header>
        <div style={{ display: 'flex', justifyContent: 'center' }}>
          <div className="box" style={{ width: '30rem' }}>
            {messages.length > 0 && (
              <div>
                {messages.map((message, index) => (
                  <p key={index}>{message}</p>
                ))}
              </div>
            )}
            <form onSubmit={handleSubmit}>
              <input
                type="email"
                name="email"
                placeholder="Email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              <br />
              <input
                type="password"
                name="password"
                placeholder="Password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <br />
              <div style={{ display: 'flex', justifyContent: 'center' }}>
                <button type="submit" className="btn btn-primary btn-block btn-large">
                  Let me in.
                </button>
              </div>
            </form>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer id="footer">
        <div className="inner">
          <ul className="icons">
            <li><a href="#" className="icon brands fa-twitter"><span className="label">Twitter</span></a></li>
            <li><a href="#" className="icon brands fa-facebook-f"><span className="label">Facebook</span></a></li>
            <li><a href="#" className="icon brands fa-instagram"><span className="label">Instagram</span></a></li>
            <li><a href="#" className="icon brands fa-github"><span className="label">GitHub</span></a></li>
            <li><a href="#" className="icon brands fa-linkedin-in"><span className="label">LinkedIn</span></a></li>
            <li><a href="#" className="icon solid fa-envelope"><span className="label">Envelope</span></a></li>
          </ul>
          <ul className="contact">
            <li>12345 Somewhere Road</li>
            <li>Nashville, TN 00000</li>
            <li>(000) 000-0000</li>
          </ul>
          <ul className="links">
            <li><a href="#">FAQ</a></li>
            <li><a href="#">Support</a></li>
            <li><a href="#">Terms</a></li>
            <li><a href="#">Contact</a></li>
          </ul>
          <p className="copyright">&copy; Untitled. All rights reserved. Lorem ipsum dolor.</p>
        </div>
      </footer>

      {/* External Scripts */}
      <script src="static/assets/js/jquery.min.js"></script>
      <script src="static/assets/js/jquery.scrollex.min.js"></script>
      <script src="static/assets/js/browser.min.js"></script>
      <script src="static/assets/js/breakpoints.min.js"></script>
      <script src="static/assets/js/util.js"></script>
      <script src="static/assets/js/main.js"></script>
    </div>
  );
}

export default App;
