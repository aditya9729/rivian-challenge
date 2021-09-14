# Rivian Digital Manufacturing Engineering DevOps Challenge

Your mission, should you choose to accept it, is to help us find a solution to move data off of a system that was provided to us by one of our many vendors. Unfortunately, we can't change that system's code, but we can partially bring it into the future by running it in Kubernetes ☸️.


## Pika's Predicament

Pika, one of our feline data scientists is also bit of a jack of all trades and started putting a few things together for you but, being a data scientist (and a cat) wasn't sure how to continue making progress. Pika has put together a skeletal Kubernetes deployment and figured out that when the `file-writer` container runs, it writes seems to periodically write data files to `/var/file-writer/data`. Pika really wishes those files would be available in an S3 bucket so they can be analyzed. Pika, being a wise cat, is also worried that if this `file-writer` keeps running forever, it might run out of storage. After 1 day (we have 2x 12-hour production shifts in the factory) and assuming the files are securely in s3, there's really no need for them locally on the container. 

Pika wasn't sure what to do next and so relieved you're able to help.

## Deliverables

To keep permissions and sharing simple, please archive your git repo containing your solution.  

Assume that we will be running this on our local machines and in a staging environment where there may already be a *large* number of files locally in `/var/file-writer/data` and in the s3 bucket. We also want to avoid uploading files needlessly if they've already been uploaded.


**Time constraints**
We want to strike a balance between giving you a chance to share your knowledge and not take up too much time on this problem. In the interest of fairness to other candidates, we ask that you try and limit your time to ~ 4 hours. If you find yourself pressed for time and need to take shortcuts, jot down a few notes about what you'd do better if you had more time. 

For example:
> - I would harden the k8s deployment by doing … because …
> - I would simplify the local dev setup by using … because …

**README.md**

Describe your solution in `README.md` file. Follow your judgement for git repo documentation best practices. Be sure to include instructions on how Pika should run the tests and the app. Follow your judgement for code and documentation best practices.

**S3 Uploader Application**

We need some sort of automated solution to the problem above. The `file-writer` is an important piece of software in the factory so if your code crashes or needs to restart, it shouldn't also take down the `file-writer` instance. We're not sure yet what s3 location we'll be using so that will need to be customizable. Pika was also asking for AWS credentials over slack but wonders if there might be a more secure way of configuring things?

**Local Dev Setup**

How should we run this locally? This can be a mix of automation (e.g. docker compose, minikube, skaffold, …) and documentation. 

**Capacity Planning**
Pika's confirmed that operators in the factory might need to check the local files during their shift but don't care about files after that. Unfortunately, operators don't have access to s3. There are 2, 12-hour shifts per day. 

We'd like to use as little local disk as possible. How much local storage should we allocate?  We'd also like to help the networking team understand how much bandwidth they should allocate.

Pika wants to moonlight as a data-engineer so be sure to briefly describe how you figured out this capacity plan.

**Monitoring**
Pika wants to be able to know if the data is flowing. What are some important metrics we should be tracking? At the very least, include those metrics in log statements.

**Idealized Architecture**
You might have taken some pragmatic shortcuts but after working through this problem you might also have a bunch of great ideas about a more ideal architecture. Jot down a couple paragraphs outlining your proposal for how things could be improved.
