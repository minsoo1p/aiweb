import React from 'react';

function App() {
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
          <h2>Usage Information</h2>
          <p>Lorem justo in tellus aenean lacinia felis.</p>
        </header>
        <div className="inner">
          <p className="guide-intro">Welcome to the AutoAngle user guide. This guide will walk you through the essential steps to effectively use our AI-driven orthopedic X-ray analysis service. Follow these instructions to get the most out of AutoAngle and streamline your radiological workflow.</p>

          <div className="instruction-container">
            {/* Instruction Box 1 */}
            <div className="instruction-box">
              <div className="instruction-content">
                <h3>1. Sign Up and Sign In</h3>
                <p>Sign up with your own name, e-mail, password. Then login to start your project!</p>
              </div>
              <div className="instruction-video">
                <video autoPlay loop muted playsInline>
                  <source src="static/videos/1.SignUp.mp4" type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              </div>
            </div>

            {/* Instruction Box 2 */}
            <div className="instruction-box">
              <div className="instruction-content">
                <h3>2. Create a Project</h3>
                <p>Enter a project name and description and create your project!</p>
              </div>
              <div className="instruction-video">
                <video autoPlay loop muted playsInline>
                  <source src="static/videos/2.Project.mp4" type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              </div>
            </div>

            {/* Instruction Box 3 */}
            <div className="instruction-box">
              <div className="instruction-content">
                <h3>3. Upload your files</h3>
                <p>After setting the X-ray area and view, drag or upload your file to upload it.</p>
              </div>
              <div className="instruction-video">
                <video autoPlay loop muted playsInline>
                  <source src="static/videos/3.FileUpload.mp4" type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              </div>
            </div>

            {/* Instruction Box 4 */}
            <div className="instruction-box">
              <div className="instruction-content">
                <h3>4. Review and Confirm Results</h3>
                <p>After processing, review the AI-generated measurements and analysis. You can make adjustments if necessary before finalizing the results.</p>
              </div>
              <div className="instruction-video">
                <video autoPlay loop muted playsInline>
                  <source src="static/videos/4.Modify.mp4" type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              </div>
            </div>

            {/* Instruction Box 5 */}
            <div className="instruction-box">
              <div className="instruction-content">
                <h3>5. Export the Results</h3>
                <p>Export your results in various formats for integration with other systems or for record-keeping. You can also share results directly with colleagues or patients.</p>
              </div>
              <div className="instruction-video">
                <video autoPlay loop muted playsInline>
                  <source src="static/videos/5.Export.mp4" type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              </div>
            </div>
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

      {/* Scripts */}
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
