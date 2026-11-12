# Easy set-up: start here if you are not technical

This page gets the job search assistant working on your computer. You do not need to
know anything about computers beyond opening a program and copying and pasting.

**You will not type any code.** You install one program, copy two messages from this
page into it, and click **Allow** when it asks. The program does the rest.

**You cannot break anything by following this page.** If something looks wrong, there
is a [what to do if you get stuck](#if-you-get-stuck) section at the bottom.

## What you need

- A Windows or Mac computer.
- A **ChatGPT** account or a **Claude** account. One is enough. If you already pay for
  one of them, use that one.
- Your CV as a file on this computer (PDF or Word).
- About an hour. Most of it is waiting while things download, and you can walk away
  during that.

**About cost.** A free ChatGPT account can start, but it runs out quickly. Most people
use a paid plan (ChatGPT Plus, or Claude Pro), which start at about US$20 a month.
Claude needs a paid plan for this. The job search assistant itself is free.

## What you will see

Both programs look roughly like this drawing. Yours will look a little different, but
the same four things are there.

![A simplified drawing of the app: a folder name, a box to type in, a New chat button, and an Allow button](docs/media/setup-app-sketch.webp)

---

## Step 1. Install the AI program

Pick **one** of these. Do not install both.

### If you use ChatGPT

1. Go to **[chatgpt.com/download](https://chatgpt.com/download/)**.
2. Click the black **Download** button and open the file it downloads. Say yes to
   whatever it asks, until ChatGPT opens.

   ![The ChatGPT download page, with the black Download button](docs/media/setup-chatgpt-download.webp)

3. Sign in with your ChatGPT account.
4. Near the top of the window there is a menu that says **ChatGPT**. Click it and
   choose **Codex**. (Codex is the part of ChatGPT that can do work on your computer.)

### If you use Claude

1. Go to **[claude.com/download](https://claude.com/download)**.
2. Click the black **Download** button and open the file it downloads. Say yes to
   whatever it asks, until Claude opens.

   ![The Claude download page, with the black Download button](docs/media/setup-claude-download.webp)

3. Sign in with your Claude account.
4. At the top of the left-hand side, click **Code**. If it asks you to upgrade, you
   need a paid Claude plan before you can continue.

## Step 2. Make a folder called Job Search

This is where the assistant and all your applications will live.

- **Windows:** Open **File Explorer** (the yellow folder icon at the bottom of the
  screen). Click **Documents** on the left. Right-click an empty white area, choose
  **New**, then **Folder**. Type `Job Search` and press Enter.
- **Mac:** Open **Finder** (the smiling face icon). Click **Documents** on the left.
  In the menu at the very top of the screen, click **File**, then **New Folder**. Type
  `Job Search` and press Return.

## Step 3. Open that folder in the AI program

- **ChatGPT (Codex):** Click **Add new project**, then find **Documents**, click
  **Job Search** once, and click the button to open or select it.
- **Claude:** Under the box where you type, click the small folder button, choose
  **Open folder…**, find **Documents**, click **Job Search** once, and click the
  button to open or select it.

If it asks whether to trust or allow access to this folder, say **yes**.

You should now see the name **Job Search** somewhere near the box where you type
(number 1 in the drawing above).

## Step 4. Copy the first message and send it

Copy everything in the grey box below. (Move your mouse over the box and click the
small copy button that appears in its top-right corner.) Then click in the typing box
in the AI program, paste, and press Enter.

```text
Set up the Job Search Agent Harness in this folder. I am not technical: do every step
you can yourself, and tell me in plain everyday words when I need to click or type
something. Do not ask me to choose between technical options; pick the recommended one.

1. Download https://github.com/WilliamEbong/job-search-agent-harness into this folder
   itself, not a subfolder. Use git if it is installed; otherwise download the ZIP and
   unpack it here (on Windows, unblock the unpacked files).
2. Run `python harness_setup.py --yes` here. If Python is missing, install it first.
3. For anything the installer reports MISSING, install it with the command it prints,
   then run the installer again. Repeat until it says all required prerequisites are
   in place.
4. If something needs my computer password or a window I must click, tell me exactly
   what to do and wait for me.
5. When everything is ready, tell me in one short sentence that step 4 of the easy
   set-up guide is finished and I can go on to step 5.
```

## Step 5. Click Allow while it works

The program now downloads the assistant and installs what it needs. This takes 10 to
40 minutes.

- It will stop several times and ask permission to download or install something.
  **Click Allow (or Approve, or Yes) every time.** This is normal and expected.
- Windows may show a separate window asking "Do you want to allow this app to make
  changes?" Click **Yes**. A Mac may ask for the password you use to log in to the
  computer. Type it.
- You will see a lot of text scroll past. You do not need to read it.
- You can leave it running and come back. If it is waiting for you, it will say so at
  the bottom.

It is finished when it tells you step 4 is done.

## Step 6. Close the program and open it again

Close the AI program completely, then open it again. This lets it notice everything
that was just installed.

## Step 7. Start a new chat and send the second message

1. Click **New chat** (in Claude it may say **New** or **New session**).
2. Check that it still says **Job Search** near the typing box. If it does not, open
   the folder again as you did in step 3.
3. Copy the grey box below, paste it, and press Enter.

```text
I am not technical. First check that everything this folder needs is installed: run
`python harness_setup.py --doctor --quick`. If anything required is missing, install
it yourself and check again, telling me in plain everyday words if I need to click
something. When everything required is in place, set me up.
```

## Step 8. Answer its questions

It now asks you a few things, one at a time. Type your answers in ordinary words.

- **Which plan you have.** Say what you pay for, for example "ChatGPT Plus" or "Claude
  Pro". If you do not know, say "I don't know, pick the cheaper option".
- **Your CV.** Tell it where the file is, for example "it's in Downloads, called
  My CV.pdf". You can also paste the text of your CV.
- **A few questions about you**, such as where you can work and the lowest pay you
  would accept. If you are unsure about one, say "skip".
- **If it asks about internet access for job searches** (ChatGPT only), choose
  **"approve each search"**.

When it has finished, it shows you the 20 kinds of job you are best suited for. You are
set up.

---

## After that, just talk to it

Open the AI program, make sure it says **Job Search**, and type any of these:

- "find me jobs"
- "apply to this", followed by a link to a job advert (or the number of a job from its
  list)
- "I applied", once you have sent an application
- "what should I do today?"

**It never sends anything to an employer.** It writes your CV and cover letter and
saves them in **Documents → Job Search → documents → applications**. You read them,
and you send them yourself.

### Prefer buttons to typing? (Windows only)

Once the steps above are done, there is also an app with buttons called **Candor**. In
your **Job Search** folder, double-click **Install Candor**. After that, open it with
the **Candor** icon on your Desktop.

![Candor's Today screen, showing one next action and the strongest jobs found](docs/media/candor-today.webp)

The names on that screen belong to a made-up example person, not a real one.

---

## If you get stuck

Nothing here can harm your computer, and you can always start a step again.

- **Ask the program itself.** It can see what went wrong. Paste this:

  ```text
  I am following the easy set-up guide (START-HERE-EASY-SETUP.md) and I am stuck.
  Look at what has happened so far, tell me in plain everyday words what went wrong,
  and fix it yourself if you can. If I must do something, give me one step at a time.
  ```

- **You cannot find a button this page mentions.** These programs change their look
  often. Type this into the program: "How do I open a folder on my computer in this
  app?" (or whatever you are looking for).
- **It says you have reached a limit.** Your plan has run out of use for now. Wait
  until the time it shows, then open the same chat and type "continue".
- **It seems to have stopped.** Scroll to the bottom. If there is an **Allow** button,
  click it. If not, type "continue".
- **Still stuck.** Take a picture of the screen with your phone and send it to the
  person who gave you this page.

## Is this safe?

- Your CV and applications stay in the **Job Search** folder on your own computer.
  There is no website holding them.
- The AI program (ChatGPT or Claude) reads them in order to help you, the same as when
  you paste something into a chat with it.
- Nothing is ever sent to an employer for you.
- To remove everything, delete the **Job Search** folder.

Comfortable with a terminal? The shorter technical instructions are in the
[README](README.md#prefer-a-terminal-or-chat).
