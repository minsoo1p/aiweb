import React, { useState, useRef } from 'react';
import Header from './components/Header';
import Menu from './components/Menu';
import Footer from './components/Footer';

const FileComponent = ({ currentUser, projects, files, project_id }) => {
  const [fileList, setFileList] = useState([]);
  const fileInputRef = useRef(null);

  const handleFileSelect = (event) => {
    const selectedFiles = event.target.files;
    setFileList([...selectedFiles]);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setFileList([...e.dataTransfer.files]);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  return (
    <div className="is-preload">
      <Header />
      <Menu projects={projects} />

      <section style={{ padding: '8rem' }}>
        <h2>{currentUser.name}'s Ongoing Files</h2>
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th style={{ width: '2rem' }}></th>
                <th>Location</th>
                <th>Type</th>
                <th>Number of Images</th>
                <th>Last Updated</th>
                <th>Angles</th>
                <th style={{ width: '8rem' }}></th>
                <th style={{ width: '2rem' }}></th>
              </tr>
            </thead>
            <tbody>
              {files.map((file) => (
                <tr key={file.id}>
                  <td>
                    <a href="#" className="fa-solid fa-square-minus"></a>
                  </td>
                  <td>{file.name1}</td>
                  <td>{file.name2}</td>
                  <td>{file.image_number}</td>
                  <td>{file.file_time}</td>
                  <td>
                    <div style={{ whiteSpace: 'nowrap', overflowX: 'auto' }}>
                      {file.selected_angles.map((angle, idx) => (
                        <ul key={idx} style={{ display: 'inline', paddingRight: '1em' }}>{angle}</ul>
                      ))}
                    </div>
                  </td>
                  <td>
                    <button className="button" onClick={() => console.log('Run Inference')}>
                      <i className="fa-solid fa-circle-play fa-lg"></i>Run
                    </button>
                  </td>
                  <td>
                    <a href="#" className="fa-solid fa-chevron-right"></a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <br />
          <h2>Adding New Files</h2>
          <form method="POST" action="#">
            <div className="container">
              <div className="row">
                <div className="col-3 col-8-small">
                  <select name="location" required>
                    <option value="" selected disabled hidden>Location</option>
                    <option value="Foot">Foot</option>
                    <option value="Ankle">Ankle</option>
                    {/* Add other options here */}
                  </select>
                </div>

                <div className="col-3 col-8-small">
                  <select name="view" required>
                    <option value="" selected disabled hidden>Type Of Image</option>
                    <option value="AnteroPosterior">AnteroPosterior</option>
                    <option value="Lateral">Lateral</option>
                    {/* Add other options here */}
                  </select>
                </div>

                <div className="col-3 col-8-small">
                  <div className="dropzone" onDrop={handleDrop} onDragOver={handleDragOver}>
                    <div style={{ paddingTop: '0.5rem' }}>
                      Drag & Drop Files here or
                      <input
                        type="file"
                        name="files[]"
                        ref={fileInputRef}
                        multiple
                        onChange={handleFileSelect}
                        style={{ display: 'none' }}
                      />
                      <button type="button" onClick={() => fileInputRef.current.click()}>
                        Browse Files
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div className="row" style={{ paddingTop: '0.7rem', alignItems: 'flex-end' }}>
                <div className="col-3">
                  <button type="submit" className="button primary icon solid fa-download">
                    Upload Files
                  </button>
                </div>
              </div>
            </div>
          </form>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default FileComponent;
