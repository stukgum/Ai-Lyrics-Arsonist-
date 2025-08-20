import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()

    const response = await fetch(`${process.env.BACKEND_URL}/api/v1/upload`, {
      method: "POST",
      body: formData,
    })

    const data = await response.json()

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status })
    }

    return NextResponse.json(data)
  } catch (error) {
    console.error("Upload proxy error:", error)
    return NextResponse.json({ detail: "Upload failed" }, { status: 500 })
  }
}
