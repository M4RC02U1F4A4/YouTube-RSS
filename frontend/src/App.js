import Main from './components/Main'
import React from 'react';
import { DataProvider } from './context/Data';


function App() {

  return (
    <DataProvider>
        <div className="App">
            <Main />
        </div>
    </DataProvider>
  );
}

export default App;
