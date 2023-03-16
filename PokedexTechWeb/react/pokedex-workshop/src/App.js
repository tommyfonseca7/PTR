import React, { Component } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import "./App.css";
import "bootstrap/dist/css/bootstrap.min.css";
import Home from "./components/Home";
import Header from "./components/Header";
import Footer from "./components/Footer";
import List from "./components/List";
import Create from "./components/Create";
import About from "./components/About";

class App extends Component {
  render() {
    return (
      <div className="App">
        <Router>
          <Header />
          <div className="container">
            <Routes>
              <Route exact path="/" element={<Home />} />
              <Route path="/list" element={<List />} />
              <Route path="/create" element={<Create />} />
              <Route path="/edit" element={<Create />} />
              <Route path="/about" element={<About />} />
            </Routes>
          </div>
          <Footer />
        </Router>
      </div>
    );
  }
}

export default App;
