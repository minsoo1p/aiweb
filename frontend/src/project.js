import React, { useState } from 'react';
import Header from './components/Header';
import Menu from './components/Menu';
import Footer from './components/Footer';

const ProjectComponent = ({ currentUser, projects }) => {
  const [projectName, setProjectName] = useState('');
  const [projectDescription, setProjectDescription] = useState('');

  const handleProjectSubmit = (e) => {
    e.preventDefault();
    // Add logic for submitting project
    console.log('Project added:', projectName, projectDescription);
  };

  return (
    <div className="is-preload">
      <Header />
      <Menu projects={projects} />

      <section style={{ padding: '8rem' }}>
        <h2>{currentUser.name}'s Ongoing Projects</h2>
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th style={{ width: '2rem' }}></th>
                <th>Name</th>
                <th>Description</th>
                <th>Creating Date</th>
                <th style={{ width: '2rem' }}></th>
              </tr>
            </thead>
            <tbody>
              {projects.map((project) => (
                <tr key={project.id}>
                  <td><a href="#" className="fa-solid fa-square-minus"></a></td>
                  <td>{project.name}</td>
                  <td>{project.description}</td>
                  <td>{project.project_time}</td>
                  <td><a href="#" className="fa-solid fa-chevron-right"></a></td>
                </tr>
              ))}
            </tbody>
          </table>
          <br />
          <form onSubmit={handleProjectSubmit}>
            <div className="row gtr-uniform">
              <div className="col-4 col-12-xsmall">
                <input
                  type="text"
                  name="project-name"
                  placeholder="Name"
                  style={{ height: '4rem' }}
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                />
              </div>
              <div className="col-6 col-12-xsmall">
                <input
                  type="text"
                  name="project-description"
                  placeholder="Description"
                  style={{ height: '4rem' }}
                  value={projectDescription}
                  onChange={(e) => setProjectDescription(e.target.value)}
                />
              </div>
              <div className="col-2 col-12-xsmall">
                <button type="submit" className="button primary fit small">
                  Add Project
                </button>
              </div>
            </div>
          </form>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default ProjectComponent;
