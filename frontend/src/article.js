import React from 'react';

function App() {
  return (
    <div>
      <header id="header">
        <h1><a href="/">AutoAngle</a></h1>
        <a href="#menu">Menu</a>
      </header>

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

      <section id="main" className="wrapper">
        <header>
          <h2>Elements</h2>
          <p>Lorem justo in tellus aenean lacinia felis.</p>
        </header>
        <div className="inner">

          <section>
            <h3>Text</h3>
            <p>This is <b>bold</b> and this is <strong>strong</strong>. This is <i>italic</i> and this is <em>emphasized</em>.
              This is <sup>superscript</sup> text and this is <sub>subscript</sub> text.
              This is <u>underlined</u> and this is code: <code>for (;;) {`{ ... }`}</code>. Finally, <a href="#">this is a link</a>.
            </p>
            <h4>Blockquote</h4>
            <blockquote>Fringilla nisl. Donec accumsan interdum nisi, quis tincidunt felis sagittis eget tempus euismod.</blockquote>
            <h4>Preformatted</h4>
            <pre><code>{`i = 0;

while (!deck.isInOrder()) {
  print 'Iteration ' + i;
  deck.shuffle();
  i++;
}

print 'It took ' + i + ' iterations to sort the deck.';`}</code></pre>
          </section>

          <section>
            <h3>Lists</h3>
            <div className="row">
              <div className="col-6 col-12-medium">
                <h4>Unordered</h4>
                <ul>
                  <li>Dolor pulvinar etiam.</li>
                  <li>Sagittis adipiscing.</li>
                  <li>Felis enim feugiat.</li>
                </ul>
                <h4>Alternate</h4>
                <ul className="alt">
                  <li>Dolor pulvinar etiam.</li>
                  <li>Sagittis adipiscing.</li>
                  <li>Felis enim feugiat.</li>
                </ul>
              </div>
              <div className="col-6 col-12-medium">
                <h4>Ordered</h4>
                <ol>
                  <li>Dolor pulvinar etiam.</li>
                  <li>Etiam vel felis viverra.</li>
                  <li>Felis enim feugiat.</li>
                  <li>Dolor pulvinar etiam.</li>
                  <li>Etiam vel felis lorem.</li>
                  <li>Felis enim et feugiat.</li>
                </ol>
                <h4>Icons</h4>
                <ul className="icons">
                  <li><a href="#" className="icon brands fa-twitter"><span className="label">Twitter</span></a></li>
                  <li><a href="#" className="icon brands fa-facebook-f"><span className="label">Facebook</span></a></li>
                  <li><a href="#" className="icon brands fa-instagram"><span className="label">Instagram</span></a></li>
                  <li><a href="#" className="icon brands fa-github"><span className="label">Github</span></a></li>
                </ul>
              </div>
            </div>
          </section>

          <section>
            <h3>Table</h3>
            <h4>Default</h4>
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Description</th>
                    <th>Price</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Item One</td>
                    <td>Ante turpis integer aliquet porttitor.</td>
                    <td>29.99</td>
                  </tr>
                  <tr>
                    <td>Item Two</td>
                    <td>Vis ac commodo adipiscing arcu aliquet.</td>
                    <td>19.99</td>
                  </tr>
                  <tr>
                    <td>Item Three</td>
                    <td>Morbi faucibus arcu accumsan lorem.</td>
                    <td>29.99</td>
                  </tr>
                  <tr>
                    <td>Item Four</td>
                    <td>Vitae integer tempus condimentum.</td>
                    <td>19.99</td>
                  </tr>
                  <tr>
                    <td>Item Five</td>
                    <td>Ante turpis integer aliquet porttitor.</td>
                    <td>29.99</td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr>
                    <td colSpan="2"></td>
                    <td>100.00</td>
                  </tr>
                </tfoot>
              </table>
            </div>

            <h4>Alternate</h4>
            <div className="table-wrapper">
              <table className="alt">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Description</th>
                    <th>Price</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Item One</td>
                    <td>Ante turpis integer aliquet porttitor.</td>
                    <td>29.99</td>
                  </tr>
                  <tr>
                    <td>Item Two</td>
                    <td>Vis ac commodo adipiscing arcu aliquet.</td>
                    <td>19.99</td>
                  </tr>
                  <tr>
                    <td>Item Three</td>
                    <td>Morbi faucibus arcu accumsan lorem.</td>
                    <td>29.99</td>
                  </tr>
                  <tr>
                    <td>Item Four</td>
                    <td>Vitae integer tempus condimentum.</td>
                    <td>19.99</td>
                  </tr>
                  <tr>
                    <td>Item Five</td>
                    <td>Ante turpis integer aliquet porttitor.</td>
                    <td>29.99</td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr>
                    <td colSpan="2"></td>
                    <td>100.00</td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </section>

          <section>
            <h3>Form</h3>
            <form method="post" action="#">
              <div className="row gtr-uniform">
                <div className="col-6 col-12-xsmall">
                  <label htmlFor="demo-name">Name</label>
                  <input type="text" name="demo-name" id="demo-name" />
                </div>
                <div className="col-6 col-12-xsmall">
                  <label htmlFor="demo-email">Email</label>
                  <input type="email" name="demo-email" id="demo-email" />
                </div>
                <div className="col-12">
                  <label htmlFor="demo-category">Category</label>
                  <select name="demo-category" id="demo-category">
                    <option value="">-</option>
                    <option value="1">Manufacturing</option>
                    <option value="1">Shipping</option>
                    <option value="1">Administration</option>
                    <option value="1">Human Resources</option>
                  </select>
                </div>
                <div className="col-4 col-12-small">
                  <input type="radio" id="demo-priority-low" name="demo-priority" defaultChecked />
                  <label htmlFor="demo-priority-low">Low Priority</label>
                </div>
                <div className="col-4 col-12-small">
                  <input type="radio" id="demo-priority-normal" name="demo-priority" />
                  <label htmlFor="demo-priority-normal">Normal Priority</label>
                </div>
                <div className="col-4 col-12-small">
                  <input type="radio" id="demo-priority-high" name="demo-priority" />
                  <label htmlFor="demo-priority-high">High Priority</label>
                </div>
                <div className="col-6 col-12-small">
                  <input type="checkbox" id="demo-copy" name="demo-copy" />
                  <label htmlFor="demo-copy">Email me a copy</label>
                </div>
                <div className="col-6 col-12-small">
                  <input type="checkbox" id="demo-human" name="demo-human" defaultChecked />
                  <label htmlFor="demo-human">Not a robot</label>
                </div>
                <div className="col-12">
                  <label htmlFor="demo-message">Message</label>
                  <textarea name="demo-message" id="demo-message" rows="6"></textarea>
                </div>
                <div className="col-12">
                  <ul className="actions">
                    <li><input type="submit" value="Send Message" className="primary" /></li>
                    <li><input type="reset" value="Reset" /></li>
                  </ul>
                </div>
              </div>
            </form>
          </section>

          <section>
            <h3>Image</h3>
            <h4>Fit</h4>
            <div className="box alt">
              <div className="row gtr-uniform">
                <div className="col-12"><span className="image fit"><img src="images/pic09.jpg" alt="" /></span></div>
                <div className="col-4"><span className="image fit"><img src="images/pic05.jpg" alt="" /></span></div>
                <div className="col-4"><span className="image fit"><img src="images/pic06.jpg" alt="" /></span></div>
                <div className="col-4"><span className="image fit"><img src="images/pic07.jpg" alt="" /></span></div>
              </div>
            </div>
            <h4>Left &amp; Right</h4>
            <p><span className="image left"><img src="images/pic01.jpg" alt="" /></span>
              Morbi mattis mi consectetur tortor elementum, varius pellentesque velit convallis...
            </p>
            <p><span className="image right"><img src="images/pic02.jpg" alt="" /></span>
              Vestibulum ultrices risus velit, sit amet blandit massa auctor sit amet...
            </p>
          </section>

        </div>
      </section>

      <footer id="footer">
        <div className="inner">
          <ul className="icons">
            <li><a href="#" className="icon brands fa-twitter"><span className="label">Twitter</span></a></li>
            <li><a href="#" className="icon brands fa-facebook-f"><span className="label">Facebook</span></a></li>
            <li><a href="#" className="icon brands fa-instagram"><span className="label">Instagram</span></a></li>
            <li><a href="#" className="icon brands fa-github"><span className="label">GitHub</span></a></li>
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
