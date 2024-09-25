import React from "react";
import { Link } from "react-router-dom";
import Banner from "./components/Banner";

const Home = ({ currentUser }) => {
  return (
    <div>
      <Banner currentUser={currentUser} />

      {/* Section One */}
      <section id="one" className="wrapper style1 split">
        <div className="inner">
          <div className="content">
            <h2>
              Lorem ipsum accumsan nisl feugiat
              <br />
              sed consequat adipiscing
            </h2>
            <p>Amet lorem vivamus viverra, quis semper consequat...</p>
            <ul className="actions">
              <li>
                <a href="#" className="button">
                  Our Story
                </a>
              </li>
            </ul>
          </div>
          <div className="image-circles">
            <div className="images">
              <span className="image">
                <img src="/static/images/pic01.jpg" alt="" />
              </span>
              <span className="image">
                <img src="/static/images/pic02.jpg" alt="" />
              </span>
            </div>
            <div className="images">
              <span className="image">
                <img src="/static/images/pic03.jpg" alt="" />
              </span>
              <span className="image">
                <img src="/static/images/pic04.jpg" alt="" />
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Section Two */}
      <section id="two" className="wrapper style2">
        <div className="inner">
          <header className="major">
            <h2>Gravida nunc accumsan</h2>
            <p>Ipsum quis semper consequat, sem nibh mattis arcu...</p>
          </header>
          <div className="features">
            <section>
              <span className="icon solid major fa-tag"></span>
              <h3>Quam adipiscing</h3>
              <p>Feugiat lorem quis semper...</p>
            </section>
            <section>
              <span className="icon solid major fa-camera-retro"></span>
              <h3>Semper accumsan</h3>
              <p>Feugiat lorem quis semper...</p>
            </section>
            <section>
              <span className="icon solid major fa-cloud"></span>
              <h3>Ipsum lorem magna</h3>
              <p>Feugiat lorem quis semper...</p>
            </section>
            <section>
              <span className="icon solid major fa-cube"></span>
              <h3>Tempus sed mattis</h3>
              <p>Feugiat lorem quis semper...</p>
            </section>
            <section>
              <span className="icon solid major fa-file-alt"></span>
              <h3>Odio fermentum</h3>
              <p>Feugiat lorem quis semper...</p>
            </section>
            <section>
              <span className="icon solid major fa-plane"></span>
              <h3>Risus et interdum</h3>
              <p>Feugiat lorem quis semper...</p>
            </section>
          </div>
          <footer className="major">
            <ul className="actions special">
              <li>
                <a href="#" className="button major">
                  More Features
                </a>
              </li>
            </ul>
          </footer>
        </div>
      </section>

      {/* Section Three */}
      <section id="three" className="wrapper style1">
        <div className="inner">
          <div className="spotlights">
            <section>
              <span className="image">
                <img src="/static/images/pic05.jpg" alt="" />
              </span>
              <div className="content">
                <h2>Convallis integer iaculis</h2>
                <p>Donec elementum odio...</p>
              </div>
            </section>
            <section>
              <span className="image">
                <img src="/static/images/pic06.jpg" alt="" />
              </span>
              <div className="content">
                <h2>Ultrices augue faucibus</h2>
                <p>Donec elementum odio...</p>
              </div>
            </section>
            <section>
              <span className="image">
                <img src="/static/images/pic07.jpg" alt="" />
              </span>
              <div className="content">
                <h2>Integer sed sodales</h2>
                <p>Donec elementum odio...</p>
              </div>
            </section>
          </div>
        </div>
      </section>

      {/* Section Four */}
      <section id="four" className="wrapper style2 special">
        <div className="inner">
          <header>
            <h2>Sed vitae massa curabitur</h2>
            <p>Ipsum quis semper consequat, sem nibh mattis arcu...</p>
          </header>
          <ul className="actions special">
            {currentUser?.isAuthenticated ? (
              <li>
                <Link to="/project" className="button primary major">
                  Get Started
                </Link>
              </li>
            ) : (
              <li>
                <Link to="/login" className="button primary major">
                  Get Started
                </Link>
              </li>
            )}
          </ul>
        </div>
      </section>
    </div>
  );
};

export default Home;
