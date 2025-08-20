export default function AccountPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Account Settings</h1>

        <div className="grid gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border">
            <h2 className="text-xl font-semibold mb-4">Profile Information</h2>
            <p className="text-gray-600 dark:text-gray-300">
              Account management features will be available once authentication is implemented.
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border">
            <h2 className="text-xl font-semibold mb-4">Usage Statistics</h2>
            <p className="text-gray-600 dark:text-gray-300">
              Track your lyric generations, exports, and usage limits here.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
