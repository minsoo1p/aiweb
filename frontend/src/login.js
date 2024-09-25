import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import "./static/assets/css/main.css";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [messages, setMessages] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const response = await fetch("/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();

    if (data.success) {
      // 로그인 성공 시 처리
      window.location.href = "/project"; // 로그인 후 리다이렉트 경로
    } else {
      // 오류 메시지 처리
      setMessages([data.message]);
    }
  };

  return (
    <div className="is-preload">
      {/* Header */}
      <header id="header">
        <h1>
          <Link to="/">AutoAngle</Link>
        </h1>
        <a href="#menu">Menu</a>
      </header>

      {/* Menu */}
      <nav id="menu">
        <ul className="links">
          <li>
            <Link to="/">Home</Link>
          </li>
          <li>
            <Link to="/info">Usage Information</Link>
          </li>
          <li>
            <Link to="/article">Related Article</Link>
          </li>
        </ul>
        <ul className="actions stacked">
          <li>
            <Link to="/register" className="button primary fit">
              Sign Up
            </Link>
          </li>
          <li>
            <Link to="/login" className="button fit">
              Log In
            </Link>
          </li>
        </ul>
      </nav>

      {/* Main Section */}
      <section id="main" className="wrapper">
        <header>
          <h2>Login</h2>
          <p>Lorem justo in tellus aenean lacinia felis.</p>
        </header>
        <div style={{ display: "flex", justifyContent: "center" }}>
          <div className="box" style={{ width: "30rem" }}>
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
                required="required"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              <br />
              <input
                type="password"
                name="password"
                placeholder="Password"
                required="required"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <br />
              <div style={{ display: "flex", justifyContent: "center" }}>
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
            <li>
              <a href="#" className="icon brands fa-twitter">
                <span className="label">Twitter</span>
              </a>
            </li>
            <li>
              <a href="#" className="icon brands fa-facebook-f">
                <span className="label">Facebook</span>
              </a>
            </li>
            <li>
              <a href="#" className="icon brands fa-instagram">
                <span className="label">Instagram</span>
              </a>
            </li>
            <li>
              <a href="#" className="icon brands fa-github">
                <span className="label">GitHub</span>
              </a>
            </li>
            <li>
              <a href="#" className="icon brands fa-linkedin-in">
                <span className="label">LinkedIn</span>
              </a>
            </li>
            <li>
              <a href="#" className="icon solid fa-envelope">
                <span className="label">Envelope</span>
              </a>
            </li>
          </ul>
          <ul className="contact">
            <li>12345 Somewhere Road</li>
            <li>Nashville, TN 00000</li>
            <li>(000) 000-0000</li>
          </ul>
          <ul className="links">
            <li>
              <a href="#">FAQ</a>
            </li>
            <li>
              <a href="#">Support</a>
            </li>
            <li>
              <a href="#">Terms</a>
            </li>
            <li>
              <a href="#">Contact</a>
            </li>
          </ul>
          <p className="copyright">&copy; Untitled. All rights reserved. Lorem ipsum dolor.</p>
        </div>
      </footer>
    </div>
  );
};

export default Login;
