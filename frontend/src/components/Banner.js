import React from "react";
import { Link } from "react-router-dom";

const Banner = ({ currentUser }) => (
  <section id="banner">
    <div className="inner">
      <div className="content">
        <h2>AutoAngle</h2>
        <p>AI-Driven fully automated service for Precise Orthopedic X-ray image Analysis</p>
      </div>
      <ul className="actions stacked">
        {currentUser?.isAuthenticated ? (
          <li><Link to="/project" className="button primary major">Get Started</Link></li>
        ) : (
          <li><Link to="/login" className="button primary major">Get Started</Link></li>
        )}
        <li><Link to="/info" className="button major">More Info</Link></li>
      </ul>
    </div>
  </section>
);

export default Banner;
