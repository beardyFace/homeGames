// Button
import * as React from 'react';

export default class Button extends React.Component {

    render() {
        const caption = this.props.caption
        const onclick = this.props.onclick
        return(
            <div>
                <button onClick={onclick}>{caption}</button>  
            </div>
        );
    }
}