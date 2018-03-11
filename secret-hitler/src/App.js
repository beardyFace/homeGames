import React, { Component } from 'react';
import './App.css';
import SecretHitlerTitle from './assets/SecretHitlerTitle.png';
import Game from './pages/game.js';

class App extends Component {
  render() {
    return (
      <div className="App">
        <div className="App-header">
          <img className ="App-title" src={SecretHitlerTitle} alt='Secret Hitler'/>
        </div>
        <div className="App-Content">
          <Game/>
        </div>
      </div>
    );
  }
}

export default App;
