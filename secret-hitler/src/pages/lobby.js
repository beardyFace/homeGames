import * as React from 'react';
import Button from '../Componants/button';

export default class Lobby extends React.Component {
    render() {
      return <Button caption='Join' onclick={() => {(alert("Player Joined"))}}/>;
    }
  }

