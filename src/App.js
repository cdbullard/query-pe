import React, { useState, useEffect, useRef } from 'react';
import Switch from 'react-switch';
import Popup from 'reactjs-popup';
import Relation from './Relation';
import Join from './Join';
import MermaidGraph from './MermaidGraphHelper';
import './App.css';
import 'bulma/css/bulma.css';

function App() {
  const [inputQuery, setInputQuery] = useState("");
  const [toggle, setToggle] = useState(true);
  const [diagram, setDiagram] = useState(`graph LR\nA-->B; Example;\n\n`);
  const [showGraph, setShowGraph] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const aboutStatement = "Query Purpose Extractor (QPE) is an undertaking to demonstrate the potential benefit \
  of parsing English meaning out of Structured Query Language (SQL) statements. \
  The motivator for this tool is to make database queries more understandable by non-technical users and \
  users who are beginning their data analytics or software development journeys.";
  const invalidResponse = "Invalid SQL Entry. Please make sure your query is in PostgreSQL format.";
  let allRelations = [];
  let allJoins = [];
  let divCounter = 0;
  
  const handleOpenModal = () => {
    setShowModal(true);
  }

  const handleCloseModal = () => {
    setShowModal(false);
  }

  const handleToggleSwitch = () => {
    setToggle(!toggle);
  }

  const handleInputChange = (e) => {
    setInputQuery(e.target.value);
  }

  const jsonIterate = (obj) => {
    Object.keys(obj).forEach(key => {
      if (key == "relname") {
        Object.values(obj[key]).forEach(value => {
          if (!allRelations.find(el => el.name === value[1])) {
            allRelations.push(new Relation(value[1], value[0]));
          }
        });
      } else if (key == "joinvalue") {
        Object.values(obj[key]).forEach(value => {
          let curSize = value.length - 1;
          let curJoin = new Join(value[0]);
          allJoins.push(curJoin);

          Object.values(value).forEach((note, index) => {
            if (index === curSize) {
              curJoin.joinType = note;
            }
            else {
              if (index === 1 && index < curSize) {
                curJoin.left.alias = note;
              }
              if (index === 2 && index < curSize && !(note in curJoin.left.attributes)) {
                curJoin.left.attributes.push(note);
              }
              if (index === 3 && index < curSize) {
                curJoin.right.alias = note;
              }
              if (index === 4 && index < curSize && !(note in curJoin.right.attributes)) {
                curJoin.right.attributes.push(note);
              }
            }
          });

          let leftTable = allRelations.find(el => el.alias == curJoin.left.alias);
          let rightTable = allRelations.find(el => el.alias == curJoin.right.alias);
          leftTable.joined = true;
          rightTable.joined = true;
        });
      } else if (key == "targets") {
        Object.values(obj[key]).forEach(value => {
          if (allRelations.find(el => el.alias === value[0])) {
            let curRelation = allRelations.find(el => el.alias === value[0]);
            if (!(value[1] in curRelation.attributes)) {
              curRelation.attributes.push(value[1]);
            }
            if (!(value[1] in curRelation.projections)) {
              curRelation.projections.push(value[1]);
            }
          }
        });
      } else if (typeof obj[key] === "object" && obj[key] !== null) {
        jsonIterate(obj[key]);
      }
    });
  }

  // TODO
  // Handle if a table originally visited as a left table appears again in another table using a different attribute
  const completeRelations = () => {
    let visited = [];

    Object.keys(allJoins).forEach(key => {
      let curLeftRelation = allRelations.find(el => el.alias === allJoins[key].left.alias);
      let curRightRelation = allRelations.find(el => el.alias === allJoins[key].right.alias);

      if (curLeftRelation && !(curLeftRelation in visited)) {
        curLeftRelation.attributes.concat(allJoins[key].left.attributes);
        allJoins[key].left = curLeftRelation;
      }
      if (curRightRelation && !(curRightRelation in visited)) {
        curRightRelation.attributes.concat(allJoins[key].right.attributes);
        allJoins[key].right = curRightRelation;
      }
    });
  }

  const createGraph = () => {
    let graphBuilder = ``;

    Object.keys(allRelations).forEach(key => {
      if (allRelations[key].joined) {
        let relatedJoin = allJoins.find(el => el.left.name === allRelations[key].name || el.right.name === allRelations[key].name);
        let matchedRelation = relatedJoin.left.name === allRelations[key].name ? relatedJoin.right.name : relatedJoin.left.name;
        graphBuilder += `${allRelations[key].name}==>${relatedJoin.joinType};\n${matchedRelation}==>${relatedJoin.joinType};\n`
      } else {
        Object.keys(allRelations[key].projections).forEach(select => {
          graphBuilder += `${allRelations[key].name}==>${allRelations[key].projections[select]};\n`;
        });
      }
    });
  
    let graphEnd = `
        
    `;

    setDiagram(`graph BT;` + `\n` + graphBuilder + graphEnd);
  }

  const handleParseRequest = async (e) => {
    e.preventDefault();
    let route = "/parse"
    let request = {};
    request.inputQuery = inputQuery;
    request.path = toggle ? 2 : 1;
    try {
      let res = await fetch(route, {
        method: "POST",
        body: JSON.stringify(request),
      });
      let result = await res.json();
      if (res.status === 200) {
        let clauseDict = result.dict;
        let outputJson = result.output;
        let responseError = (String(outputJson).includes("Invalid") || String(outputJson).includes("undefined"));

        if (toggle) {
          document.getElementById("resultBox").value = outputJson;
        } else {
          try {
            var formattedJson = JSON.stringify(JSON.parse(outputJson), undefined, 2);
            document.getElementById("resultBox").value = formattedJson;
          } catch {
            document.getElementById("resultBox").value = invalidResponse;
          }
        }
        
        if (responseError) {
          setShowGraph(false);
          document.getElementById("resultBox").value = invalidResponse;
        } else {
          // Rebuild Relations and Joins
          allRelations = [];
          allJoins = []
          jsonIterate(clauseDict);
          completeRelations();
          createGraph();
          setShowGraph(true);
        }
      } else {
        window.alert("An error has occurred. Please verify your query and try again.");
        setShowGraph(false);
      }
    } catch (err) {
      console.log(err);
    }
  };

  return (
    <div className="App">
      <section className="hero is-primary is-small">
          <div className="hero-body">
              <p className="title">Query Purpose Extractor</p>
          </div>
      </section>

      <nav className="navbar" role="navigation" aria-label="main navigation">
        <div className="navbar-brand">
          <a role="button" className="navbar-burger" aria-label="menu" aria-expanded="false">
            <span aria-hidden="true"></span>
            <span aria-hidden="true"></span>
            <span aria-hidden="true"></span>
          </a>
        </div>
        <div id="navbarBasic" className="navbar-menu is-active">
          <div className="navbar-start">
            <a className="navbar-item" onClick={handleOpenModal}>
              About
            </a>
            <a className="navbar-item" href="https://github.com/cdbullard/query-pe" target="_blank">
              Documentation (GitHub)
            </a>
            <a className="navbar-item" href="https://github.com/cdbullard/query-pe/issues/new" target="_blank">
              Report Issue
            </a>
          </div>
          <div className="navbar-end" />
        </div>
      </nav>

      <div className="body">
        <div className="container">
          <section className="section">
            <div className="columns">
              <div className="column is-half">
                <div className="field">
                  <label className="label">SQL Input</label>
                  <div className="control">
                    <textarea className="textarea is-primary has-fixed-size formatted-textarea is-size-6 has-text-grey-dark"
                        onChange={handleInputChange}
                        placeholder="Enter SQL Query for Parsing"
                        rows={12}
                        id="inputQuery"
                      />
                  </div>
                </div>
                <div className="field is-pulled-left">
                  <label className="label is-small">
                    <span>
                      {toggle ? "Generate Parsed Results" : "Generate JSON Tree"}
                    </span>
                  </label>
                  <div className="control">
                    <Switch onChange={handleToggleSwitch} checked={toggle} />
                  </div>
                </div>
                <div className="field is-pulled-right">
                  <div className="control">
                    <button 
                      className="button is-link is-light is-success is-normal"
                      type="submit"
                      onClick={handleParseRequest}>Submit
                    </button>
                  </div>
                </div>
              </div>

              <div className="column is-half">
                <label className="label">Parsed Output</label>
                <div className="control">
                  <textarea className="textarea is-primary has-fixed-size formatted-textarea is-size-6 has-text-grey-dark has-background-white-ter"
                      id="resultBox"
                      readOnly
                      placeholder="Results Will Appear Here"
                      rows={12}
                      />
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
      <div className="container">
        <div id="mermaidDiv" key={divCounter}>
          {showGraph ? <MermaidGraph graphDefinition={diagram} /> : null}
        </div>
      </div>

      <Popup open={showModal} onClose={handleCloseModal}>{aboutStatement}</Popup>
    </div>
  );
}

export default App;