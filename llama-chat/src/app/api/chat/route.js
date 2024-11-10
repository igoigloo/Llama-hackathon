import { NextResponse } from 'next/server'

export async function POST(req) {
  const body = await req.json()
  const { messages } = body

  const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ messages }),
  })

  if (!response.ok) {
    return NextResponse.json({ error: 'Error from backend' }, { status: 500 })
  }

  const data = response.body
  return new NextResponse(data, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-transform',
      'Connection': 'keep-alive',
    },
  })
}