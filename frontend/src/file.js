import React, { useState } from 'react';

function App() {
  const [files, setFiles] = useState([]);

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setFiles(e.dataTransfer.files);
  };

  const handleFileChange = (e) => {
    setFiles(e.target.files);
  };

  const handleSubmit = (e) => {
    if (files.length === 0) {
      e.preventDefault();
      alert('Please select at least one file.');
    }
  };

  return (
    <div className="is-preload">
      {/* Header */}
      <header id="header">
        <h1><a href="/">AutoAngle</a></h1>
        <a href="#menu">Projects</a>
      </header>

      {/* Menu */}
      <nav id="menu">
        <ul className="links">
          <li><a href="/">Home</a></li>
          <li><a href="/projects">All Projects</a></li>
          {/* Replace the following with actual project rendering */}
          <li><a href="/file/1">Sample Project</a></li>
        </ul>
        <ul className="actions stacked">
          <li><a href="/logout" className="button primary fit">Logout</a></li>
        </ul>
      </nav>

      {/* Main Section */}
      <section style={{ padding: '8rem' }}>
        <h2>User's Ongoing Files</h2>
        <br />
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th style={{ width: '2rem' }}></th>
                <th>Location</th>
                <th>Type</th>
                <th>Number of Images</th>
                <th>Last Updated</th>
                <th style={{ width: '2rem' }}></th>
              </tr>
            </thead>
            <tbody>
              {/* Example row */}
              <tr>
                <td><a href="/delete" className="fa-solid fa-square-minus"></a></td>
                <td>Foot</td>
                <td>AnteroPosterior</td>
                <td>5</td>
                <td>2023-09-21</td>
                <td style={{ textAlign: 'right' }}><a href="/processing" className="fa-solid fa-chevron-right"></a></td>
              </tr>
            </tbody>
          </table>

          <br />
          <br />
          <br />
          <h2>Adding New Files</h2>
          <form onSubmit={handleSubmit} encType="multipart/form-data">
            <div className="container">
              <div className="row">
                <div className="col-3 col-12-xsmall">
                  <select name="location" id="location">
                    <option value="">Location</option>
                    <option value="Foot">Foot</option>
                    <option value="Ankle">Ankle</option>
                    {/* Add more options as needed */}
                  </select>
                </div>

                <div className="col-3 col-12-xsmall">
                  <select name="view" id="view">
                    <option value="">Type Of Image</option>
                    <option value="AnteroPosterior">AnteroPosterior</option>
                    <option value="Lateral">Lateral</option>
                    {/* Add more options as needed */}
                  </select>
                </div>
              </div>

              <div className="row" style={{ paddingTop: '0.7rem' }}>
                <div className="col-6">
                  <div
                    id="dropzone"
                    className="dropzone"
                    onDragOver={handleDragOver}
                    onDrop={handleDrop}
                    style={{
                      border: '2px dashed #cccccc',
                      padding: '20px',
                      textAlign: 'center',
                      color: '#888888',
                      width: '100%',
                    }}
                  >
                    파일을 마우스로 끌어 오세요
                  </div>
                </div>
                <div className="col-2 col-12-xsmall">
                  <input
                    type="file"
                    name="files[]"
                    id="file-input"
                    accept="image/*"
                    multiple
                    onChange={handleFileChange}
                  />
                </div>
                <div className="col-3 col-12-xsmall">
                  <button type="submit" className="button primary icon solid fa-download">Upload Files</button>
                </div>
              </div>
            </div>
          </form>
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
}

export default App;
