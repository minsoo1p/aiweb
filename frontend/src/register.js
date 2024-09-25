import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const Register = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [messages, setMessages] = useState([]);

  const handleSubmit = async (e) => {
	e.preventDefault();
  
	try {
	  const response = await fetch('/register', {
		method: 'POST',
		headers: {
		  'Content-Type': 'application/json',
		},
		body: JSON.stringify({ name, email, password }),
	  });
  
	  // 응답의 Content-Type 확인
	  const contentType = response.headers.get('content-type');
	  if (contentType && contentType.includes('application/json')) {
		const data = await response.json(); // JSON 응답 파싱
		if (response.ok) {
		  setMessages([data.message || 'Registration successful']);
		} else {
		  setMessages([data.error || 'Registration failed']);
		}
	  } else {
		// JSON이 아닌 경우
		setMessages(['Unexpected response format.']);
	  }
	} catch (error) {
	  console.error('Error:', error);
	  setMessages(['An error occurred. Please try again.']);
	}
  };
  

  return (
    <div className="is-preload">
      {/* Header */}
      <header id="header">
        <h1><Link to="/">AutoAngle</Link></h1>
        <a href="#menu">Menu</a>
      </header>

      {/* Menu */}
      <nav id="menu">
        <ul className="links">
          <li><Link to="/">Home</Link></li>
          <li><Link to="/info">Usage Information</Link></li>
          <li><Link to="/article">Related Article</Link></li>
        </ul>
        <ul className="actions stacked">
          <li><Link to="/register" className="button primary fit">Sign Up</Link></li>
          <li><Link to="/login" className="button fit">Log In</Link></li>
        </ul>
      </nav>

      {/* Main */}
      <section id="main" className="wrapper">
        <header>
          <h2>Register</h2>
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
                type="text"
                name="name"
                placeholder="Name"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
              <br />
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
                  Sign me up.
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
    </div>
  );
};

export default Register;
