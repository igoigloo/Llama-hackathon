'use client'

import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card"

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [darkMode, setDarkMode] = useState(true);

  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const newMessage = { role: 'user', content: input };
    setMessages([...messages, newMessage]);
    setInput('');

    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ messages: [...messages, newMessage] }),
    });

    if (response.ok) {
      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let done = false;
      let accumulatedResponse = '';

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        const chunk = decoder.decode(value, { stream: true });
        accumulatedResponse += chunk;

        // Update the last AI message with the accumulated response
        setMessages((prevMessages) => {
          const lastMessage = prevMessages[prevMessages.length - 1];
          if (lastMessage && lastMessage.role === 'ai') {
            return [
              ...prevMessages.slice(0, -1),
              { role: 'ai', content: accumulatedResponse },
            ];
          } else {
            return [...prevMessages, { role: 'ai', content: accumulatedResponse }];
          }
        });
      }
    } else {
      console.error('Error fetching response from backend');
    }
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  return (
    <div className={`relative flex items-center justify-center min-h-screen ${darkMode ? 'bg-gray-900' : 'bg-gray-100'}`}>
      <Button 
        onClick={toggleDarkMode} 
        className="absolute top-4 right-4"
      >
        {darkMode ? 'Light Mode' : 'Dark Mode'}
      </Button>
      <Card className={`w-[600px] h-[700px] ${darkMode ? 'bg-gray-800 text-white' : 'bg-white text-black'}`}>
        <CardHeader>
          <CardTitle>Chat</CardTitle>
        </CardHeader>
        <CardContent className="overflow-y-auto h-[calc(100%-120px)]">
          <div className="space-y-4">
            {messages.map((m, index) => (
              <div key={index} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'} items-center`}>
                <div className={`w-3 h-3 rounded-full mr-2 ${m.role === 'user' ? 'bg-blue-500' : 'bg-green-500'}`}></div>
                <div className={`rounded-lg p-2 ${m.role === 'user' ? (darkMode ? 'bg-blue-700' : 'bg-blue-500') : (darkMode ? 'bg-gray-700' : 'bg-gray-200')}`}>
                  {m.content}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
        <CardFooter>
          <form onSubmit={handleSubmit} className="flex w-full space-x-2">
            <Input
              value={input}
              onChange={handleInputChange}
              placeholder="Type a message..."
              className={darkMode ? 'bg-gray-700 text-white' : ''}
            />
            <Button type="submit">Send</Button>
          </form>
        </CardFooter>
      </Card>
    </div>
  );
}
